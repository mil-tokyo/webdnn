///<reference path="../../dist/webdnn.umd.d.ts" />

'use strict';
declare const WebGPUComputeCommandEncoder;
declare const WebAssembly;

type ModelName = 'squeeze_net' | 'resnet50' | 'vgg16' | 'inception_v3';
type FrameworkName = 'WebDNN' | 'keras.js' | 'deeplearn.js';

const InputSize: { [key in ModelName]: number} = {
    'squeeze_net': 227,
    'resnet50': 224,
    'vgg16': 224,
    'inception_v3': 299,
};

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
    framework: FrameworkName,
    modelName: ModelName,
    iteration: number
    batchSize: number
}

class Benchmark<C extends Configuration> {
    summary: Summary | null = null;
    configuration: C;

    async runAsync(configuration: C) {
        this.configuration = configuration;

        await this.setupAsync();
        let results = await this.executeAsync();
        await this.finalizeAsync();

        return this.summarize(results);
    }

    /**
     * Setup model
     * @returns {Promise<void>}
     */
    async setupAsync() {
        throw Error("Not Implemented");
    }

    async executeAsync() {
        let results: number[] = [];

        for (let i = 0; i < this.configuration.iteration; i++) {
            this.onExecuteSingle(i);
            await new Promise(resolve => requestAnimationFrame(resolve));

            let tStart = performance.now();
            await this.executeSingleAsync();
            let elapsedTime = performance.now() - tStart;

            results.push(elapsedTime);
        }

        return results;
    }

    /**
     * Execute model
     * @returns {Promise<void>}
     */
    async executeSingleAsync() {
        throw Error('Not Implemented');
    }

    /**
     * Finalize
     * @returns {Promise<void>}
     */
    async finalizeAsync() {
    }

    summarize(results: number[]) {
        results.shift(); // remove first run, which is regarded as "warming up" execution

        let d = results.reduce((d, v) => {
            d.sum += v;
            d.sum2 += v * v;
            return d;
        }, {sum: 0, sum2: 0});

        let mean = d.sum / results.length;
        let std = Math.sqrt((d.sum2 - results.length * mean * mean) / (results.length - 1));

        return {
            configuration: this.configuration,
            mean: mean,
            std: std,
            results: results
        };
    }

    onExecuteSingle(iteration: number) {
    }
}

//---------------------------------------------------------------------------------------------------
//
// WebDNN
//

interface WebDNNConfiguration extends Configuration {
    framework: 'WebDNN',
    backend: WebDNN.BackendName,
    optimize: boolean
}

class WebDNNBenchmark extends Benchmark<WebDNNConfiguration> {
    runner: WebDNN.DescriptorRunner<WebDNN.GraphDescriptor> | null = null;

    async setupAsync() {
        let url = `./output/webdnn/${this.configuration.modelName}/${this.configuration.optimize ? '' : 'non_'}optimized`;
        this.runner = await WebDNN.load(url, {
            backendOrder: [this.configuration.backend]
        });
    }

    async executeSingleAsync() {
        return await this.runner!.run();
    }

    async finalizeAsync() {
        this.runner = null;
    }
}

//---------------------------------------------------------------------------------------------------
//
// KerasJS
//

declare namespace KerasJS {
    type Model = any;
}
declare const KerasJS: any;

interface KerasJSConfiguration extends Configuration {
    framework: 'keras.js'
    gpu: boolean
}

class KerasJSBenchmark extends Benchmark<KerasJSConfiguration> {
    model: KerasJS.Model | null = null;
    xs: { [name: string]: Float32Array } | null;

    setupAsync() {
        if (this.configuration.batchSize !== 1) {
            throw Error('Keras.js benchmark supports only batchsize=1.');
        }

        let prefix = `./output/kerasjs/${this.configuration.modelName}/model`;
        this.model = new KerasJS.Model({
            filepaths: {
                model: `${prefix}.json`,
                weights: `${prefix}_weights.buf`,
                metadata: `${prefix}_metadata.json`
            },
            gpu: this.configuration.gpu
        });

        const S = InputSize[this.configuration.modelName];
        this.xs = {
            'input_1': new Float32Array(this.configuration.batchSize * S * S * 3)
        };

        return this.model.ready()
    }

    async executeSingleAsync() {
        return this.model!.predict(this.xs!);
    }

    async finalizeAsync() {
        this.model = null;
        this.xs = null;
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

interface DeepLearnJSConfiguration extends Configuration {
    framework: 'deeplearn.js',
    gpu: boolean
}

class DeepLearnJSBenchmark extends Benchmark<DeepLearnJSConfiguration> {
    math: deeplearn.NDArrayMath | null = null;
    parameters: deeplearn.NDArray[][] | null = null;
    xs: deeplearn.NDArray[] | null;

    async setupAsync() {
        if (this.configuration.modelName !== 'resnet50') {
            throw Error('Only ResNet50 is supported in benchmark of deeplearn.js');
        }
        this.math = this.configuration.gpu ? new deeplearn.NDArrayMathGPU() : new deeplearn.NDArrayMathCPU();
        this.xs = [];
        this.math!.scope((keep) => {
            for (let n = 0; n < this.configuration.batchSize; n++) {
                let x = deeplearn.Array3D.randNormal([225, 225, 3]);
                keep(x);
                this.xs.push(x);
            }
        })
    }

    async executeSingleAsync() {
        let xs = this.xs;
        let ys = [];

        this.math!.scope((keep) => {
            // Dispatch
            switch (this.configuration.modelName) {
                case 'resnet50':
                    for (let n = 0; n < this.configuration.batchSize; n++) {
                        ys.push(this.resnet50(xs[n], keep));
                    }
                    break;

                default:
                    throw Error(`Not supported: ${this.configuration.modelName}`);
            }

            for (let y of ys) y.getValues();
        });

    }

    private resnet50(x, keep) {
        let math = this.math!;
        let parameters = this.parameters || (this.parameters = []);
        let counter = 0;

        function getParameter(factory: () => deeplearn.NDArray[]) {
            if (counter === parameters.length) {
                let newParameters = factory();
                newParameters.forEach(keep);
                parameters.push(newParameters);
            }
            return parameters[counter++];
        }

        function bn(x: deeplearn.NDArray) {
            let [scale, bias] = getParameter(() => ([
                deeplearn.Array3D.zeros(x.shape as [number, number, number]),
                deeplearn.Array3D.zeros(x.shape as [number, number, number])
            ]));

            return math.add(math.multiply(x, scale), bias);
        }

        function conv2d(x: deeplearn.NDArray, outChannel: number, ksize: number, stride: number, padding: number) {
            let [w, b] = getParameter(() => ([
                deeplearn.Array4D.zeros([ksize, ksize, x.shape[2], outChannel]),
                deeplearn.Array1D.zeros([outChannel])
            ]));

            return math.conv2d(x, w, b, stride, padding);
        }

        function relu(x: deeplearn.NDArray) {
            return math.relu(x);
        }

        function block(x: deeplearn.NDArray, outChannel: number, stride: number = 1) {
            let h1 = (x.shape[2] == outChannel && stride === 1) ?
                x :
                bn(conv2d(x, outChannel, stride, stride, 0));

            let h2 = relu(bn(conv2d(x, outChannel / 4, stride, stride, 0)));

            h2 = relu(bn(conv2d(h2, outChannel / 4, 3, 1, 1)));
            h2 = bn(conv2d(h2, outChannel, 1, 1, 0));

            return relu(math.add(h1, h2));
        }

        function dense(x: deeplearn.NDArray, outChannel: number) {
            let [w] = getParameter(() => ([
                deeplearn.Array2D.randNormal([x.shape[1], outChannel])
            ]));

            return math.matMul(x, w);
        }

        // Conv 1.x 225 -> 112
        let h11 = relu(bn(conv2d(x, 64, 7, 2, 3)));

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
        let h6 = math.maxPool(h53, 7, 7, 0).reshape([1, 2048]); // Because deeplearn.js doesn't support average pooling, use max pooling instead.
        let y = dense(h6, 1000);

        return y;
    }

    async finalizeAsync() {
        this.math = null;
        this.parameters = null;
        this.xs = null;
    }
}

//---------------------------------------------------------------------------------------------------
//
// Main
//

const BenchmarkClass: { [key in FrameworkName] : { new(): Benchmark<Configuration> }} = {
    'WebDNN': WebDNNBenchmark,
    'keras.js': KerasJSBenchmark,
    'deeplearn.js': DeepLearnJSBenchmark
};

async function run() {
    let logger = new Logger(document.querySelector('#log') as HTMLPreElement);
    logger.group('Benchmark');

    try {
        let configuration = JSON.parse((document.querySelector('#configurations') as HTMLSelectElement).selectedOptions[0].value) as Configuration;

        configuration.modelName = (document.querySelector('#modelName') as HTMLSelectElement).selectedOptions[0].value as ModelName;
        configuration.iteration = Number((document.querySelector('#iteration') as HTMLInputElement).value) + 1;
        configuration.batchSize = Number((document.querySelector('#batchSize') as HTMLInputElement).value);

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
        let benchmark = new BenchmarkClass[configuration.framework]();
        benchmark.onExecuteSingle = (i => logger.log(`Iteration: ${i + 1} / ${configuration.iteration}`));
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
    let webdnnConfigurations: WebDNNConfiguration[] = [{
        framework: 'WebDNN',
        name: 'WebDNN (WebGPU backend)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        optimize: false,
        backend: 'webgpu'
    }, {
        framework: 'WebDNN',
        name: 'WebDNN (WebGPU backend + Optimize)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        optimize: true,
        backend: 'webgpu'
    }, {
        framework: 'WebDNN',
        name: 'WebDNN (WebGL backend)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        optimize: false,
        backend: 'webgl'
    }, {
        framework: 'WebDNN',
        name: 'WebDNN (WebGL backend + Optimize)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        optimize: true,
        backend: 'webgl'
    }, {
        framework: 'WebDNN',
        name: 'WebDNN (WebAssembly backend)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        optimize: false,
        backend: 'webassembly'
    }, {
        framework: 'WebDNN',
        name: 'WebDNN (WebAssembly backend + Optimize)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        optimize: true,
        backend: 'webassembly'
    }];
    let kerasjsConfigurations: KerasJSConfiguration[] = [{
        framework: 'keras.js',
        name: 'keras.js (CPU)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        gpu: false
    }, {
        framework: 'keras.js',
        name: 'keras.js (GPU)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        gpu: true
    }];
    let deeplearnjsConfigurations: DeepLearnJSConfiguration[] = [{
        framework: 'deeplearn.js',
        name: 'deeplearn.js (CPU)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        gpu: false
    }, {
        framework: 'deeplearn.js',
        name: 'deeplearn.js (GPU)',
        modelName: 'resnet50',
        batchSize: 0,
        iteration: 0,
        gpu: true
    }];

    let configurations: Configuration[] = [];
    configurations = configurations.concat(webdnnConfigurations, kerasjsConfigurations, deeplearnjsConfigurations);

    for (let configuration of configurations) {
        let option = document.createElement('option');
        option.value = JSON.stringify(configuration);
        option.textContent = configuration.name;

        if (configuration.framework === 'WebDNN') {
            if (!WebDNN.getBackendAvailability().status[(configuration as WebDNNConfiguration).backend]) {
                option.disabled = true;
            }
        }

        document.querySelector('#configurations').appendChild(option);
    }

    let button = (document.querySelector('#runButton') as HTMLButtonElement);
    button.disabled = false;
    button.addEventListener('click', run);
});
