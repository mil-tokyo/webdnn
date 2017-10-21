///<reference path="../../dist/webdnn.umd.d.ts" />
'use strict';
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
class Logger {
    constructor($dom) {
        this.$dom = $dom;
        this.indent = 0;
    }
    log(message) {
        console.log(message);
        this.$dom.textContent += `\n${'\t'.repeat(this.indent) + message}`;
    }
    error(err) {
        console.error(err);
        this.$dom.textContent += `\n${'\t'.repeat(this.indent) + err.message}`;
    }
    group(name) {
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
class Benchmark {
    constructor(logger) {
        this.logger = logger;
        this.summary = null;
    }
    runAsync(configuration) {
        return __awaiter(this, void 0, void 0, function* () {
            this.configuration = configuration;
            yield this.setupAsync();
            this.timer = this.getGLContext().getExtension('EXT_disjoint_timer_query');
            if (!this.timer) {
                this.timer = this.getGLContext().getExtension('EXT_disjoint_timer_query_webgl2');
                if (!this.timer)
                    throw Error('No EXT_disjoint_timer_query is available');
            }
            let results = yield this.executeAsync();
            yield this.finalizeAsync();
            return this.summarize(results);
        });
    }
    /**
     * Setup model
     * @returns {Promise<WebGLRenderingContext>}
     */
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            throw Error("Not Implemented");
        });
    }
    executeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            let results = [];
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
                        yield new Promise(r => setTimeout(r));
                    }
                    let duration = timer.getQueryObjectEXT(query, timer.QUERY_RESULT_EXT) * 1e-6;
                    results.push(duration / this.configuration.iteration);
                    timer.deleteQueryExt(query);
                }
            }
            else if (gl instanceof WebGL2RenderingContext) {
                for (let j = 0; j < this.configuration.testIteration; j++) {
                    let query = gl.createQuery();
                    this.onExecuteSingle(results.length);
                    for (let i = 0; i < this.configuration.warmupIteration; i++) {
                        yield this.executeSingleAsync();
                    }
                    gl.beginQuery(timer.TIME_ELAPSED_EXT, query);
                    for (let i = 0; i < this.configuration.iteration; i++) {
                        yield this.executeSingleAsync();
                    }
                    gl.endQuery(timer.TIME_ELAPSED_EXT);
                    function check() {
                        const available = gl.getQueryParameter(query, gl.QUERY_RESULT_AVAILABLE);
                        const disjoint = gl.getParameter(timer.GPU_DISJOINT_EXT);
                        return available && !disjoint;
                    }
                    while (!check()) {
                        yield new Promise(r => setTimeout(r));
                    }
                    let duration = gl.getQueryParameter(query, gl.QUERY_RESULT) * 1e-6;
                    results.push(duration / this.configuration.iteration);
                    gl.deleteQuery(query);
                }
            }
            return results;
        });
    }
    /**
     * Finalize
     * @returns {Promise<void>}
     */
    finalizeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
        });
    }
    summarize(results) {
        let d = results.reduce((d, v) => {
            d.sum += v;
            d.sum2 += v * v;
            return d;
        }, { sum: 0, sum2: 0 });
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
    onExecuteSingle(iteration) {
        this.logger.log(`Iteration: ${iteration + 1} / ${this.configuration.testIteration}`);
    }
}
//---------------------------------------------------------------------------------------------------
//
// WebDNN
//
class WebDNNBenchmark extends Benchmark {
    constructor() {
        super(...arguments);
        this.runner = null;
    }
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.runner = yield WebDNN.load('./webdnn_model', {
                backendOrder: ['webgl']
            });
        });
    }
    getGLContext() {
        return this.runner.handler.gl;
    }
    executeSingleAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            return this.runner.run();
        });
    }
    finalizeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.runner = null;
        });
    }
}
class DeepLearnJSBenchmark extends Benchmark {
    constructor() {
        super(...arguments);
        this.parameters = [];
    }
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.math = new deeplearn.NDArrayMathGPU();
            this.gpgpu = this.math.getGPGPUContext();
            this.math.scope((keep) => {
                this.x = deeplearn.Array3D.randNormal([225, 225, 3]);
                keep(this.x);
            });
        });
    }
    getGLContext() {
        return this.gpgpu.gl;
    }
    executeSingleAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.math.scope((keep) => {
                let math = this.math;
                let parameters = this.parameters;
                let counter = 0;
                function getParameter(factory) {
                    if (counter === parameters.length) {
                        let newParameters = factory();
                        newParameters.map(keep);
                        parameters.push(newParameters);
                    }
                    return parameters[counter++];
                }
                function bn(x) {
                    let [scale, bias] = getParameter(() => ([
                        deeplearn.Array3D.zeros(x.shape),
                        deeplearn.Array3D.zeros(x.shape)
                    ]));
                    return math.batchNormalization3D(x, scale, bias);
                }
                function conv2d(x, outChannel, ksize, stride, padding) {
                    let [w, b] = getParameter(() => ([
                        deeplearn.Array4D.zeros([ksize, ksize, x.shape[2], outChannel]),
                        deeplearn.Array1D.zeros([outChannel])
                    ]));
                    return math.conv2d(x, w, b, stride, padding);
                }
                function block(x, outChannel, stride = 1) {
                    let h1 = (x.shape[2] == outChannel && stride === 1) ?
                        x :
                        bn(conv2d(x, outChannel, stride, stride, 0));
                    let h2 = math.relu(bn(conv2d(x, outChannel / 4, stride, stride, 0)));
                    h2 = math.relu(bn(conv2d(h2, outChannel / 4, 3, 1, 1)));
                    h2 = bn(conv2d(h2, outChannel, 1, 1, 0));
                    return math.relu(math.add(h1, h2));
                }
                function dense(x, outChannel) {
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
        });
    }
    finalizeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.math = null;
            this.parameters = null;
            this.x = null;
        });
    }
}
//---------------------------------------------------------------------------------------------------
//
// Main
//
function run() {
    return __awaiter(this, void 0, void 0, function* () {
        let logger = new Logger(document.querySelector('#log'));
        logger.group('Benchmark');
        try {
            let configuration = JSON.parse(document.querySelector('#configurations').selectedOptions[0].value);
            configuration.warmupIteration = Number(document.querySelector('#warmupIteration').value);
            configuration.iteration = Number(document.querySelector('#iteration').value);
            configuration.testIteration = Number(document.querySelector('#testIteration').value);
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
            let summary = yield benchmark.runAsync(configuration);
            logger.groupEnd();
            logger.group('Result');
            logger.log(`Elapsed Time: ${summary.mean.toFixed(2)}+-${summary.std.toFixed(2)}[ms/batch]`);
            logger.groupEnd();
        }
        catch (err) {
            logger.error(err);
        }
        logger.groupEnd();
    });
}
document.addEventListener('DOMContentLoaded', () => {
    let configurations = [{
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
    let button = document.querySelector('#runButton');
    button.disabled = false;
    button.addEventListener('click', run);
});
//# sourceMappingURL=index.js.map