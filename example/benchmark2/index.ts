///<reference path="../../dist/webdnn.umd.d.ts" />

'use strict';
declare const WebGPUComputeCommandEncoder;
declare const WebAssembly;

class Logger {
    private indent = 0;

    constructor(private $dom: HTMLElement) {
    }

    log(message: any) {
        console.log(message);
        this.$dom.textContent += `\n${'\t'.repeat(this.indent) + message}`
    }

    error(err: Error) {
        console.error(err);
        this.$dom.textContent += `\n${'\t'.repeat(this.indent) + err.message}`
    }

    group(name: string) {
        console.group(name);
        this.log('');
        this.$dom.textContent += `\n${'\t'.repeat(this.indent) + name}`;
        this.indent++;
    }

    groupEnd() {
        console.groupEnd();
        this.indent--;
    }
}

interface Summary {
    name: string,
    mean: number,
    std: number,
    results: number[]
}

interface Configuration {
    name: string
    framework: string
    iteration: number
    testIteration: number
    warmupIteration: number
}

abstract class Benchmark {
    summary: Summary | null = null;
    configuration: Configuration;
    timer: any;

    constructor(public logger: Logger) {
    }

    async runAsync(configuration: Configuration) {
        this.configuration = configuration;

        await this.setupAsync();

        this.timer = this.getGLContext().getExtension('EXT_disjoint_timer_query');
        if (!this.timer) {
            this.timer = this.getGLContext().getExtension('EXT_disjoint_timer_query_webgl2');
            if (!this.timer) throw Error('No EXT_disjoint_timer_query is available');
        }

        let results = await this.executeAsync();
        await this.finalizeAsync();

        return this.summarize(results);
    }

    /**
     * Setup model
     * @returns {Promise<WebGLRenderingContext>}
     */
    async setupAsync() {
        throw Error("Not Implemented");
    }

    abstract getGLContext(): WebGLRenderingContext;

    async executeAsync() {
        let results: number[] = [];
        let gl = this.getGLContext();
        let timer = this.timer;

        if (gl instanceof WebGLRenderingContext) {
            for (let j = 0; j < this.configuration.testIteration; j++) {
                let query = timer.createQueryExt();

                this.onExecuteSingle(results.length);

                for (let i = 0; i < this.configuration.warmupIteration; i++) {
                    this.executeSingleAsync();
                }

                timer.beginQueryEXT(timer.TIME_ELAPSED_EXT, query);
                for (let i = 0; i < this.configuration.iteration; i++) {
                    this.executeSingleAsync();
                }
                timer.endQueryEXT(timer.TIME_ELAPSED_EXT);

                function check() {
                    const available = timer.getQueryObjectEXT(query, timer.QUERY_RESULT_AVAILABLE_EXT);
                    const disjoint = gl.getParameter(timer.GPU_DISJOINT_EXT);
                    return available && !disjoint;
                }

                while (!check()) {
                    await new Promise(r => setTimeout(r))
                }

                let duration = timer.getQueryObjectEXT(query, timer.QUERY_RESULT_EXT) * 1e-6;
                results.push(duration / this.configuration.iteration);

                timer.deleteQueryExt(query);
            }
        } else if (gl instanceof WebGL2RenderingContext) {
            for (let j = 0; j < this.configuration.testIteration; j++) {
                let query = (gl as any).createQuery();

                this.onExecuteSingle(results.length);

                for (let i = 0; i < this.configuration.warmupIteration; i++) {
                    await this.executeSingleAsync();
                }

                (gl as any).beginQuery(timer.TIME_ELAPSED_EXT, query);
                for (let i = 0; i < this.configuration.iteration; i++) {
                    await this.executeSingleAsync();
                }
                (gl as any).endQuery(timer.TIME_ELAPSED_EXT);

                function check() {
                    const available = (gl as any).getQueryParameter(query, (gl as any).QUERY_RESULT_AVAILABLE);
                    const disjoint = gl.getParameter(timer.GPU_DISJOINT_EXT);
                    return available && !disjoint;
                }

                while (!check()) {
                    await new Promise(r => setTimeout(r))
                }

                let duration = (gl as any).getQueryParameter(query, (gl as any).QUERY_RESULT) * 1e-6;
                results.push(duration / this.configuration.iteration);

                (gl as any).deleteQuery(query);
            }
        }


        return results;
    }

    /**
     * Execute model
     * @returns {Promise<void>}
     */
    abstract async executeSingleAsync(): Promise<void>;

    /**
     * Finalize
     * @returns {Promise<void>}
     */
    async finalizeAsync() {
    }

    summarize(results: number[]) {
        let d = results.reduce((d, v) => {
            d.sum += v;
            d.sum2 += v * v;
            return d;
        }, {sum: 0, sum2: 0});

        let mean = d.sum / results.length;
        let std = Math.sqrt(Math.abs(d.sum2 - results.length * mean * mean) / (results.length - 1));

        let summary = {
            configuration: this.configuration,
            mean: mean,
            std: std,
            results: results
        };
        console.log(summary);
        return summary;
    }

    onExecuteSingle(iteration: number) {
        this.logger.log(`Iteration: ${iteration + 1} / ${this.configuration.testIteration}`);
    }
}

//---------------------------------------------------------------------------------------------------
//
// WebDNN
//

class WebDNNBenchmark extends Benchmark {
    runner: WebDNN.DescriptorRunner | null = null;

    async setupAsync() {
        this.runner = await WebDNN.load('./webdnn_model', {
            backendOrder: ['webgl']
        });
    }

    getGLContext(): WebGLRenderingContext {
        return (this.runner as any).handler.gl;
    }

    async executeSingleAsync() {
        return this.runner!.run();
    }

    async finalizeAsync() {
        this.runner = null;
    }
}

//---------------------------------------------------------------------------------------------------
//
// deeplearn.js
//

declare namespace deeplearn {
    type Session = any;
    type NDArray = any;
    type NDArrayMath = any;
    type Tensor = any;
}
declare const deeplearn;

class DeepLearnJSBenchmark extends Benchmark {
    math: any;
    gpgpu: any;
    parameters: deeplearn.NDArray[][] = [];
    x: any;

    async setupAsync() {
        this.math = new deeplearn.NDArrayMathGPU();
        this.gpgpu = this.math.getGPGPUContext();
        this.math!.scope((keep) => {
            this.x = deeplearn.Array3D.randNormal([225, 225, 3]);
            keep(this.x);
        });
    }

    getGLContext(): WebGLRenderingContext {
        return this.gpgpu.gl
    }

    async executeSingleAsync() {
        this.math!.scope((keep) => {
            let math = this.math!;
            let parameters = this.parameters;
            let counter = 0;

            function getParameter(factory: () => deeplearn.NDArray[]) {
                if (counter === parameters.length) {
                    let newParameters = factory();
                    newParameters.map(keep);
                    parameters.push(newParameters);
                }
                return parameters[counter++];
            }

            function bn(x: deeplearn.NDArray) {
                let [scale, bias] = getParameter(() => ([
                    deeplearn.Array3D.zeros(x.shape as [number, number, number]),
                    deeplearn.Array3D.zeros(x.shape as [number, number, number])
                ]));

                return math.batchNormalization3D(x, scale, bias);
            }

            function conv2d(x: deeplearn.NDArray, outChannel: number, ksize: number, stride: number, padding: number) {
                let [w, b] = getParameter(() => ([
                    deeplearn.Array4D.zeros([ksize, ksize, x.shape[2], outChannel]),
                    deeplearn.Array1D.zeros([outChannel])
                ]));

                return math.conv2d(x, w, b, stride, padding);
            }

            function block(x: deeplearn.NDArray, outChannel: number, stride: number = 1) {
                let h1 = (x.shape[2] == outChannel && stride === 1) ?
                    x :
                    bn(conv2d(x, outChannel, stride, stride, 0));

                let h2 = math.relu(bn(conv2d(x, outChannel / 4, stride, stride, 0)));

                h2 = math.relu(bn(conv2d(h2, outChannel / 4, 3, 1, 1)));
                h2 = bn(conv2d(h2, outChannel, 1, 1, 0));

                return math.relu(math.add(h1, h2));
            }

            function dense(x: deeplearn.NDArray, outChannel: number) {
                let [w] = getParameter(() => ([
                    deeplearn.Array2D.randNormal([x.shape[1], outChannel])
                ]));

                return math.matMul(x, w);
            }

            // Conv 1.x 225 -> 112
            let h11 = math.relu(bn(conv2d(this.x, 64, 7, 2, 3)));

            //Conv 2.x 112 -> 56
            let h20 = math.maxPool(h11, 3, 2, 0);
            let h21 = block(h20, 256);
            let h22 = block(h21, 256);
            let h23 = block(h22, 256);

            //Conv 3.x 56 -> 28
            let h31 = block(h23, 512, 2);
            let h32 = block(h31, 512);
            let h33 = block(h32, 512);
            let h34 = block(h33, 512);

            //Conv 4.x 28 -> 14
            let h41 = block(h34, 1024, 2);
            let h42 = block(h41, 1024);
            let h43 = block(h42, 1024);
            let h44 = block(h43, 1024);
            let h45 = block(h44, 1024);
            let h46 = block(h45, 1024);

            //Conv 5.x 14 -> 7
            let h51 = block(h46, 2048, 2);
            let h52 = block(h51, 2048);
            let h53 = block(h52, 2048);

            //fc
            let h6 = math.avgPool(h53, 7, 7, 0).reshape([1, 2048]);
            let y = dense(h6, 1000);
            console.log(this.parameters.length);
        });
    }

    async finalizeAsync() {
        this.math = null;
        this.parameters = null;
        this.x = null;
    }
}

//---------------------------------------------------------------------------------------------------
//
// Main
//

async function run() {
    let logger = new Logger(document.querySelector('#log') as HTMLPreElement);
    logger.group('Benchmark');

    try {
        let configuration = JSON.parse((document.querySelector('#configurations') as HTMLSelectElement).selectedOptions[0].value) as Configuration;

        configuration.warmupIteration = Number((document.querySelector('#warmupIteration') as HTMLInputElement).value);
        configuration.iteration = Number((document.querySelector('#iteration') as HTMLInputElement).value);
        configuration.testIteration = Number((document.querySelector('#testIteration') as HTMLInputElement).value);

        logger.group('Environment Information');
        logger.log(`${'UserAgent'.padStart(12)}: ${(navigator.userAgent) || '(N/A)'}`);
        logger.log(`${'Platform'.padStart(12)}: ${(navigator.platform || '(N/A)')}`);
        logger.groupEnd();

        logger.group('Configuration');
        Object.keys(configuration).forEach(key => {
            logger.log(`${key.padStart(12)}: ${configuration[key]}`);
        });
        logger.groupEnd();

        logger.group('Run');
        let benchmark = configuration.framework === 'WebDNN' ? (new WebDNNBenchmark(logger)) : (new DeepLearnJSBenchmark(logger));
        let summary = await benchmark.runAsync(configuration);
        logger.groupEnd();

        logger.group('Result');
        logger.log(`Elapsed Time: ${summary.mean.toFixed(2)}+-${summary.std.toFixed(2)}[ms/batch]`);
        logger.groupEnd();

    } catch (err) {
        logger.error(err);
    }

    logger.groupEnd();
}

document.addEventListener('DOMContentLoaded', () => {
    let configurations: Configuration[] = [{
        framework: 'WebDNN',
        name: 'WebDNN (WebGL backend + Optimize)',
        testIteration: 0,
        iteration: 0,
        warmupIteration: 0
    }, {
        framework: 'deeplearn.js',
        name: 'deeplearn.js (GPU)',
        testIteration: 0,
        iteration: 0,
        warmupIteration: 0
    }];

    for (let configuration of configurations) {
        let option = document.createElement('option');
        option.value = JSON.stringify(configuration);
        option.textContent = configuration.name;
        document.querySelector('#configurations').appendChild(option);
    }

    let button = (document.querySelector('#runButton') as HTMLButtonElement);
    button.disabled = false;
    button.addEventListener('click', run);
});
