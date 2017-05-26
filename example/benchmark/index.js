'use strict';

function console_log(message) {
    console.log(message);
    document.getElementById('message').appendChild(
        document.createTextNode(message + "\n")
    );
}

function console_error(message) {
    console.error(message);
    document.getElementById('message').appendChild(
        document.createTextNode(message + "\n")
    );
}

class BaseBenchmark {
    constructor(name, numIteration) {
        this.name = name;
        this.numIteration = numIteration;
        this.summary = null;
    }

    runAsync() {
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
            .then(() => this.executeAsync());
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
    constructor(name, numIteration, flagGPU) {
        super(name, numIteration);
        this.model = null;
        this.flagGPU = flagGPU;
        this.xs = {
            'input_1': new Float32Array(224 * 224 * 3)
        };
    }

    setupAsync() {
        let prefix = './output/kerasjs/resnet50/model';
        this.model = new KerasJS.Model({
            filepaths: {
                model: `${prefix}.json`,
                weights: `${prefix}_weights.buf`,
                metadata: `${prefix}_metadata.json`
            },
            gpu: this.flagGPU
        });

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
    constructor(name, numIteration, backend, flagOptimized) {
        super(name, numIteration);
        this.runner = null;
        this.x = null;
        this.y = null;
        this.backend = backend;
        this.flagOptimized = flagOptimized;
    }

    setupAsync() {
        //noinspection ES6ModulesDependencies
        return WebDNN.init([this.backend])
            .then(() => {
                //noinspection ES6ModulesDependencies
                this.runner = WebDNN.gpu.createDescriptorRunner();
                return this.runner.load(`./output/webdnn/resnet50/${this.flagOptimized ? '' : 'non_'}optimized`);
            })
            .then(() => this.runner.getInputViews())
            .then(xs => {
                this.x = xs[0];
                return this.runner.getOutputViews();
            })
            .then(ys => {
                this.y = ys[0];
            })
    }

    executeSingleAsync() {
        return this.runner.run()
    }

    finalizeAsync() {
        this.runner = null;
        this.x = null;
        this.y = null;
    }
}

function run() {
    const N = 10 + 1;

    let kerasCPU = new KerasJSBenchmark('Keras.js(CPU)', N, false);
    let kerasGPU = new KerasJSBenchmark('Keras.js(GPU)', N, true);
    let webdnnNonOptimizedCPU = new WebDNNBenchmark('WebDNN(WebAssembly)', N, 'webassembly', false);
    let webdnnOptimizedCPU = new WebDNNBenchmark('WebDNN(WebAssembly) + Optimize', N, 'webassembly', true);
    let webdnnNonOptimizedGPU = new WebDNNBenchmark('WebDNN(WebGPU)', N, 'webgpu', false);
    let webdnnOptimizedGPU = new WebDNNBenchmark('WebDNN(WebGPU) + Optimize', N, 'webgpu', true);

    let summaryHandler = summary => console_log(`${summary.name} : ${summary.mean.toFixed(2)}+-${summary.std.toFixed(2)}ms`);

    console_log('Benchmark start');
    Promise.resolve()
        .then(() => kerasCPU.runAsync().then(summaryHandler))
        .then(() => kerasGPU.runAsync().then(summaryHandler))
        .then(() => webdnnNonOptimizedCPU.runAsync().then(summaryHandler))
        .then(() => webdnnOptimizedCPU.runAsync().then(summaryHandler))
        .then(() => webdnnNonOptimizedGPU.runAsync().then(summaryHandler))
        .then(() => webdnnOptimizedGPU.runAsync().then(summaryHandler))
        .then(() => console_log('Benchmark end'))
        .catch(err => console_error(err));
}
