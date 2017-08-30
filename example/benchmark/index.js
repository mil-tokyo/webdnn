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
let benchmarks = [];
function console_log(message) {
    console.log(message);
    document.getElementById('message').appendChild(document.createTextNode(message + "\n"));
}
function console_error(err) {
    console.error(err);
    document.getElementById('message').appendChild(document.createTextNode(err.message + "\n"));
}
class BaseBenchmark {
    constructor(name) {
        this.summary = null;
        this.numIteration = -1;
        this.name = name;
    }
    static getSelectedModel() {
        let model_name_selection = document.forms['benchmark'].model_name;
        let model_name = 'resnet50';
        for (let i = 0; i < model_name_selection.length; i++) {
            if (model_name_selection[i].checked) {
                model_name = model_name_selection[i].value;
            }
        }
        console_log(`Model: ${model_name}`);
        return model_name;
    }
    runAsync(numIteration) {
        return __awaiter(this, void 0, void 0, function* () {
            this.numIteration = numIteration;
            this.results = [];
            return this.setupAsync()
                .then(() => this.executeAsync())
                .then(() => this.finalizeAsync())
                .then(() => {
                let summary = this.summarize();
                this.summary = summary;
                return summary;
            })
                .catch((err) => console_error(err));
        });
    }
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            return Promise.resolve();
        });
    }
    executeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            for (let i = 0; i < this.numIteration; i++) {
                this.onExecuteSingle(i);
                yield new Promise(resolve => setTimeout(resolve, 1000));
                let tStart = performance.now();
                yield this.executeSingleAsync();
                let elapsedTime = performance.now() - tStart;
                this.results.push(elapsedTime);
            }
        });
    }
    executeSingleAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            throw Error('Not Implemented');
        });
    }
    finalizeAsync() {
        return Promise.resolve();
    }
    summarize() {
        this.results.shift(); // remove first run
        let results = this.results.sort();
        let d = results.reduce((d, v) => {
            d.sum += v;
            d.sum2 += v * v;
            return d;
        }, { sum: 0, sum2: 0 });
        let mean = d.sum / results.length;
        let std = Math.sqrt((d.sum2 - results.length * mean * mean) / (results.length - 1));
        return {
            name: this.name,
            mean: mean,
            std: std,
            results: results
        };
    }
    onExecuteSingle(i) {
        console_log(`${this.name}: ${i + 1}/${this.numIteration}`);
    }
}
class KerasJSBenchmark extends BaseBenchmark {
    constructor(name, flagGPU) {
        super(name);
        this.model = null;
        this.flagGPU = flagGPU;
    }
    setupAsync() {
        let modelName = BaseBenchmark.getSelectedModel();
        let prefix = `./output/kerasjs/${modelName}/model`;
        this.model = new KerasJS.Model({
            filepaths: {
                model: `${prefix}.json`,
                weights: `${prefix}_weights.buf`,
                metadata: `${prefix}_metadata.json`
            },
            gpu: this.flagGPU
        });
        const HW = (modelName === 'inception_v3') ? (299 * 299) : (224 * 224);
        this.xs = {
            'input_1': new Float32Array(HW * 3)
        };
        return this.model.ready();
    }
    executeSingleAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            return this.model.predict(this.xs);
        });
    }
    finalizeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.model = null;
            this.xs = null;
        });
    }
}
class WebDNNBenchmark extends BaseBenchmark {
    constructor(name, backend, flagOptimized) {
        super(name);
        this.runner = null;
        this.backend = backend;
        this.flagOptimized = flagOptimized;
    }
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            //noinspection ES6ModulesDependencies
            return WebDNN.load(`./output/webdnn/${BaseBenchmark.getSelectedModel()}/${this.flagOptimized ? '' : 'non_'}optimized`, {
                backendOrder: [this.backend]
            })
                .then((runner) => {
                this.runner = runner;
            });
        });
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
class DeepLearnJSBenchmark extends BaseBenchmark {
    constructor(name, flagUsingGPU) {
        super(name);
        this.session = null;
        this.feeds = null;
        this.math = null;
        this.y = null;
        this.flagUsingGPU = flagUsingGPU;
    }
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            if (DeepLearnJSBenchmark.getSelectedModel() !== 'resnet50') {
                throw Error('Only ResNet50 is supported in benchmark of deeplearn.js');
            }
            let graph = new deeplearn.Graph();
            let x = graph.placeholder('input', [221, 221, 3]);
            function bn(x) {
                let scale = graph.variable('s', deeplearn.Array4D.zeros(x.shape));
                let bias = graph.variable('b', deeplearn.Array4D.zeros(x.shape));
                return graph.add(graph.multiply(x, scale), bias);
            }
            function conv2d(x, outChannel, ksize = 3, stride = 1, padding = 1) {
                let w = graph.variable('w', deeplearn.Array4D.zeros([ksize, ksize, x.shape[2], outChannel]));
                let b = graph.variable('b', deeplearn.Array1D.zeros([outChannel]));
                return graph.conv2d(x, w, b, ksize, outChannel, stride, padding);
            }
            function relu(x) {
                return graph.relu(x);
            }
            function block(x, outChannel, ksize = 3, stride = 1, padding = 1) {
                let h1 = (x.shape[2] == outChannel && ksize === 3 && stride === 1 && padding === 1) ?
                    x :
                    bn(conv2d(x, outChannel, ksize, stride, padding));
                let h2 = relu(bn(conv2d(x, outChannel / 4, ksize, stride, padding)));
                h2 = relu(bn(conv2d(h2, outChannel / 4)));
                h2 = bn(conv2d(h2, outChannel));
                return relu(graph.add(h1, h2));
            }
            function dense(x, outChannel) {
                let w = graph.variable('w', deeplearn.Array2D.zeros([x.shape[0], outChannel]));
                return graph.matmul(x, w);
            }
            // Conv 1.x
            let h11 = relu(bn(conv2d(x, 64, 7, 2, 3)));
            //Conv 2.x
            let h20 = graph.maxPool(h11, 3, 2, 0);
            let h21 = block(h20, 256);
            let h22 = block(h21, 256);
            //Conv 3.x
            let h31 = block(h22, 512, 1, 2, 0);
            let h32 = block(h31, 512);
            let h33 = block(h32, 512);
            let h34 = block(h33, 512);
            //Conv 4.x
            let h41 = block(h34, 1024, 2, 2, 0);
            let h42 = block(h41, 1024);
            let h43 = block(h42, 1024);
            let h44 = block(h43, 1024);
            let h45 = block(h44, 1024);
            let h46 = block(h45, 1024);
            //Conv 5.x
            let h51 = block(h46, 2048, 2, 2, 0);
            let h52 = block(h51, 2048);
            let h53 = block(h52, 2048);
            //fc
            // Because deeplearn.js doesn't support average pool, use maxpool instead.
            let h6 = graph.reshape(graph.maxPool(h53, 7, 7, 0), [2048]);
            let y = dense(h6, 1000);
            let math = this.flagUsingGPU ?
                new deeplearn.NDArrayMathGPU() :
                new deeplearn.NDArrayMathCPU();
            let session = new deeplearn.Session(graph, math);
            this.session = session;
            this.math = math;
            this.feeds = [{
                    tensor: x,
                    data: deeplearn.Array3D.zeros([221, 221, 3])
                }];
            this.y = y;
        });
    }
    executeSingleAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.math.scope(() => {
                let yVal = this.session.eval(this.y, this.feeds).getValues();
            });
        });
    }
    finalizeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.session = null;
            this.math = null;
            this.feeds = null;
            this.y = null;
        });
    }
}
// noinspection JSUnusedLocalSymbols
function run() {
    let numIteration = Number(document.forms['benchmark'].iterations.value) + 1;
    if (isNaN(numIteration)) {
        numIteration = 5;
    }
    let mode_selection = document.forms['benchmark'].mode_selection;
    let benchmark_id = 0;
    for (let i = 0; i < mode_selection.length; i++) {
        if (mode_selection[i].checked) {
            benchmark_id = Number(mode_selection[i].value);
        }
    }
    let benchmark = benchmarks[benchmark_id];
    let summaryHandler = summary => console_log(`${summary.name} : ${summary.mean.toFixed(2)}+-${summary.std.toFixed(2)}ms`);
    console_log(`Benchmark ${benchmark.name} start`);
    Promise.resolve()
        .then(() => benchmark.runAsync(numIteration).then(summaryHandler))
        .then(() => console_log('Benchmark end'))
        .catch(err => console_error(err));
}
document.addEventListener('DOMContentLoaded', () => {
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebGPU)', 'webgpu', false));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebGPU) + Optimize', 'webgpu', true));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebAssembly)', 'webassembly', false));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebAssembly) + Optimize', 'webassembly', true));
    if (typeof WebGLRenderingContext !== 'undefined') {
        benchmarks.push(new WebDNNBenchmark('WebDNN(WebGL)', 'webgl', false));
        benchmarks.push(new WebDNNBenchmark('WebDNN(WebGL) + Optimize', 'webgl', true));
    }
    benchmarks.push(new KerasJSBenchmark('Keras.js(CPU)', false));
    benchmarks.push(new KerasJSBenchmark('Keras.js(GPU)', true));
    benchmarks.push(new DeepLearnJSBenchmark('deeplearn.js(CPU)', false));
    benchmarks.push(new DeepLearnJSBenchmark('deeplearn.js(GPU)', true));
    let div_modelist = document.getElementById('modelist');
    for (let i = 0; i < benchmarks.length; i++) {
        let benchmark = benchmarks[i];
        div_modelist.innerHTML += `<label><input type="radio" name="mode_selection" value="${i}" ${i == 0 ? 'checked' : ''}>${benchmark.name}</label><br>`;
    }
    let environment_note = "";
    if (typeof WebGPUComputeCommandEncoder === 'undefined') {
        environment_note += "This browser does not support WebGPU.\n";
    }
    if (typeof WebAssembly === 'undefined') {
        environment_note += "This browser does not support WebAssembly. WebAssembly backend will run in asm.js mode.\n";
    }
    document.getElementById('environment_note').innerHTML = environment_note;
    let button = document.getElementById('run_button');
    button.disabled = false;
    button.addEventListener('click', run);
});
