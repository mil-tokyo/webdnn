'use strict';

let benchmarks = [];

function console_log(message) {
    console.log(message);
    document.getElementById('message').appendChild(
        document.createTextNode(message + "\n")
    );
}

function console_error(message) {
    console.error(message);
    if (message.message) {
        message = message.message;
    }
    document.getElementById('message').appendChild(
        document.createTextNode(message + "\n")
    );
}

class BaseBenchmark {
    constructor(name) {
        this.name = name;
        this.summary = null;
    }

    getSelectedModel() {
        let model_name_selection = document.forms.benchmark.model_name;
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
        this.numIteration = numIteration;
        this.results = [];
        return this.setupAsync()
            .then(() => this.executeAsync())
            .then(() => this.finalizeAsync())
            .then(() => {
                let summary = this.summarize();
                this.summary = summary;

                return summary;
            });
    }

    setupAsync() {
        return Promise.resolve();
    }

    executeAsync() {
        if (this.results.length >= this.numIteration) return Promise.resolve();

        this.onExecuteSingle(this.results.length);

        let tStart = performance.now();
        return this.executeSingleAsync()
            .then(() => {
                let elapsedTime = performance.now() - tStart;
                this.results.push(elapsedTime);
            })
            .then(() => {
                return new Promise((resolve, reject) => {
                    setTimeout(() => {
                        resolve(this.executeAsync());
                    }, 10);
                })
            });
    }

    executeSingleAsync() {
        throw Error('Not Implemented');
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
        }, {sum: 0, sum2: 0});

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
        let modelName = this.getSelectedModel();
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

        return this.model.ready()
    }

    executeSingleAsync() {
        return this.model.predict(this.xs);
    }

    finalizeAsync() {
        this.model = null;
        this.xs = null;
    }
}

class WebDNNBenchmark extends BaseBenchmark {
    constructor(name, backend, flagOptimized) {
        super(name);
        this.x = null;
        this.y = null;
        this.backend = backend;
        this.flagOptimized = flagOptimized;
        this.runner = null;
    }

    setupAsync() {
        //noinspection ES6ModulesDependencies
        return WebDNN.load(`./output/webdnn/${this.getSelectedModel()}/${this.flagOptimized ? '' : 'non_'}optimized`, {backendOrder: [this.backend]})
            .then((runner) => {
                this.runner = runner;
                this.x = runner.getInputViews()[0].toActual();
                this.y = runner.getOutputViews()[0].toActual();
            })
    }

    executeSingleAsync() {
        return this.runner.run()
    }

    finalizeAsync() {
        this.x = null;
        this.y = null;
        this.runner = null;
    }
}


function run() {
    let numIteration = Number(document.forms.benchmark.iterations.value) + 1;
    if (isNaN(numIteration)) {
        numIteration = 5;
    }

    let mode_selection = document.forms.benchmark.mode_selection;
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

document.addEventListener('DOMContentLoaded', function(event) {
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebGPU) + Optimize', 'webgpu', true));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebGPU)', 'webgpu', false));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebAssembly) + Optimize', 'webassembly', true));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebAssembly)', 'webassembly', false));
    if (typeof WebGLRenderingContext !== 'undefined') {
        benchmarks.push(new WebDNNBenchmark('WebDNN(WebGL) + Optimize', 'webgl', true));
        benchmarks.push(new WebDNNBenchmark('WebDNN(WebGL)', 'webgl', false));
    }
    benchmarks.push(new KerasJSBenchmark('Keras.js(CPU)', false));
    benchmarks.push(new KerasJSBenchmark('Keras.js(GPU)', true));

    let div_modelist = document.getElementById('modelist');
    for (let i = 0; i < benchmarks.length; i++) {
        let benchmark = benchmarks[i];
        div_modelist.innerHTML += `<label><input type="radio" name="mode_selection" value="${i}" ${i == 0 ? 'checked' : ''}>${benchmark.name}</label><br>`
    }

    let environment_note = "";
    if (typeof WebGPUComputeCommandEncoder === 'undefined') {
        environment_note += "This browser does not support WebGPU.\n";
    }
    if (typeof WebAssembly === 'undefined') {
        environment_note += "This browser does not support WebAssembly. WebAssembly backend will run in asm.js mode.\n";
    }
    document.getElementById('environment_note').innerHTML = environment_note;

    document.getElementById('run_button').disabled = false;
});
