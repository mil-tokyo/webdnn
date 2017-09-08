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
const InputSize = {
    'squeeze_net': 227,
    'resnet50': 224,
    'vgg16': 224,
    'inception_v3': 299,
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
    constructor() {
        this.summary = null;
    }
    runAsync(configuration) {
        return __awaiter(this, void 0, void 0, function* () {
            this.configuration = configuration;
            yield this.setupAsync();
            let results = yield this.executeAsync();
            yield this.finalizeAsync();
            return this.summarize(results);
        });
    }
    /**
     * Setup model
     * @returns {Promise<void>}
     */
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            throw Error("Not Implemented");
        });
    }
    executeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            let results = [];
            for (let i = 0; i < this.configuration.iteration; i++) {
                this.onExecuteSingle(i);
                yield new Promise(resolve => requestAnimationFrame(resolve));
                let tStart = performance.now();
                yield this.executeSingleAsync();
                let elapsedTime = performance.now() - tStart;
                results.push(elapsedTime);
            }
            return results;
        });
    }
    /**
     * Execute model
     * @returns {Promise<void>}
     */
    executeSingleAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            throw Error('Not Implemented');
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
        results.shift(); // remove first run, which is regarded as "warming up" execution
        let d = results.reduce((d, v) => {
            d.sum += v;
            d.sum2 += v * v;
            return d;
        }, { sum: 0, sum2: 0 });
        let mean = d.sum / results.length;
        let std = Math.sqrt((d.sum2 - results.length * mean * mean) / (results.length - 1));
        return {
            configuration: this.configuration,
            mean: mean,
            std: std,
            results: results
        };
    }
    onExecuteSingle(iteration) {
    }
}
class WebDNNBenchmark extends Benchmark {
    constructor() {
        super(...arguments);
        this.runner = null;
    }
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            let url = `./output/webdnn/${this.configuration.modelName}/${this.configuration.optimize ? '' : 'non_'}optimized`;
            this.runner = yield WebDNN.load(url, {
                backendOrder: [this.configuration.backend]
            });
        });
    }
    executeSingleAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this.runner.run();
        });
    }
    finalizeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.runner = null;
        });
    }
}
class KerasJSBenchmark extends Benchmark {
    constructor() {
        super(...arguments);
        this.model = null;
    }
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
class DeepLearnJSBenchmark extends Benchmark {
    constructor() {
        super(...arguments);
        this.math = null;
        this.parameters = null;
    }
    setupAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.configuration.modelName !== 'resnet50') {
                throw Error('Only ResNet50 is supported in benchmark of deeplearn.js');
            }
            this.math = this.configuration.gpu ? new deeplearn.NDArrayMathGPU() : new deeplearn.NDArrayMathCPU();
            this.xs = [];
            this.math.scope((keep) => {
                for (let n = 0; n < this.configuration.batchSize; n++) {
                    let x = deeplearn.Array3D.randNormal([225, 225, 3]);
                    keep(x);
                    this.xs.push(x);
                }
            });
        });
    }
    executeSingleAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            let xs = this.xs;
            let ys = [];
            this.math.scope((keep) => {
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
                for (let y of ys)
                    y.getValues();
            });
        });
    }
    resnet50(x, keep) {
        let math = this.math;
        let parameters = this.parameters || (this.parameters = []);
        let counter = 0;
        function getParameter(factory) {
            if (counter === parameters.length) {
                let newParameters = factory();
                newParameters.forEach(keep);
                parameters.push(newParameters);
            }
            return parameters[counter++];
        }
        function bn(x) {
            let [scale, bias] = getParameter(() => ([
                deeplearn.Array3D.zeros(x.shape),
                deeplearn.Array3D.zeros(x.shape)
            ]));
            return math.add(math.multiply(x, scale), bias);
        }
        function conv2d(x, outChannel, ksize, stride, padding) {
            let [w, b] = getParameter(() => ([
                deeplearn.Array4D.zeros([ksize, ksize, x.shape[2], outChannel]),
                deeplearn.Array1D.zeros([outChannel])
            ]));
            return math.conv2d(x, w, b, stride, padding);
        }
        function relu(x) {
            return math.relu(x);
        }
        function block(x, outChannel, stride = 1) {
            let h1 = (x.shape[2] == outChannel && stride === 1) ?
                x :
                //@NOTE(Kiikurage): Original model use ksize=1, however deeplearn.js cannot handle this value.
                bn(conv2d(x, outChannel, stride, stride, 0));
            let h2 = relu(bn(conv2d(x, outChannel / 4, stride, stride, 0)));
            h2 = relu(bn(conv2d(h2, outChannel / 4, 3, 1, 1)));
            h2 = bn(conv2d(h2, outChannel, 1, 1, 0));
            return relu(math.add(h1, h2));
        }
        function dense(x, outChannel) {
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
    finalizeAsync() {
        return __awaiter(this, void 0, void 0, function* () {
            this.math = null;
            this.parameters = null;
            this.xs = null;
        });
    }
}
//---------------------------------------------------------------------------------------------------
//
// Main
//
const BenchmarkClass = {
    'WebDNN': WebDNNBenchmark,
    'keras.js': KerasJSBenchmark,
    'deeplearn.js': DeepLearnJSBenchmark
};
function run() {
    return __awaiter(this, void 0, void 0, function* () {
        let logger = new Logger(document.querySelector('#log'));
        logger.group('Benchmark');
        try {
            let configuration = JSON.parse(document.querySelector('#configurations').selectedOptions[0].value);
            configuration.modelName = document.querySelector('#modelName').selectedOptions[0].value;
            configuration.iteration = Number(document.querySelector('#iteration').value) + 1;
            configuration.batchSize = Number(document.querySelector('#batchSize').value);
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
    let webdnnConfigurations = [{
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
    let kerasjsConfigurations = [{
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
    let deeplearnjsConfigurations = [{
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
    let configurations = [];
    configurations = configurations.concat(webdnnConfigurations, kerasjsConfigurations, deeplearnjsConfigurations);
    for (let configuration of configurations) {
        let option = document.createElement('option');
        option.value = JSON.stringify(configuration);
        option.textContent = configuration.name;
        if (configuration.framework === 'WebDNN') {
            if (!WebDNN.getBackendAvailability().status[configuration.backend]) {
                option.disabled = true;
            }
        }
        document.querySelector('#configurations').appendChild(option);
    }
    let button = document.querySelector('#runButton');
    button.disabled = false;
    button.addEventListener('click', run);
});
//# sourceMappingURL=index.js.map