'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var benchmarks = [];

function console_log(message) {
    console.log(message);
    document.getElementById('message').appendChild(document.createTextNode(message + "\n"));
}

function console_error(message) {
    console.error(message);
    document.getElementById('message').appendChild(document.createTextNode(message + "\n"));
}

var BaseBenchmark = function () {
    function BaseBenchmark(name) {
        _classCallCheck(this, BaseBenchmark);

        this.name = name;
        this.summary = null;
    }

    _createClass(BaseBenchmark, [{
        key: 'runAsync',
        value: function runAsync(numIteration) {
            var _this = this;

            this.numIteration = numIteration;
            this.results = [];
            return this.setupAsync().then(function () {
                return _this.executeAsync();
            }).then(function () {
                return _this.finalizeAsync();
            }).then(function () {
                var summary = _this.summarize();
                _this.summary = summary;

                return summary;
            });
        }
    }, {
        key: 'setupAsync',
        value: function setupAsync() {
            return Promise.resolve();
        }
    }, {
        key: 'executeAsync',
        value: function executeAsync() {
            var _this2 = this;

            if (this.results.length >= this.numIteration) return Promise.resolve();

            this.onExecuteSingle(this.results.length);

            var tStart = performance.now();
            return this.executeSingleAsync().then(function () {
                var elapsedTime = performance.now() - tStart;
                _this2.results.push(elapsedTime);
            }).then(function () {
                return new Promise(function (resolve, reject) {
                    setTimeout(function () {
                        resolve(_this2.executeAsync());
                    }, 10);
                });
            });
        }
    }, {
        key: 'executeSingleAsync',
        value: function executeSingleAsync() {
            throw Error('Not Implemented');
        }
    }, {
        key: 'finalizeAsync',
        value: function finalizeAsync() {
            return Promise.resolve();
        }
    }, {
        key: 'summarize',
        value: function summarize() {
            this.results.shift(); // remove first run
            var results = this.results.sort();
            var d = results.reduce(function (d, v) {
                d.sum += v;
                d.sum2 += v * v;
                return d;
            }, { sum: 0, sum2: 0 });

            var mean = d.sum / results.length;
            var std = Math.sqrt((d.sum2 - results.length * mean * mean) / (results.length - 1));

            return {
                name: this.name,
                mean: mean,
                std: std,
                results: results
            };
        }
    }, {
        key: 'onExecuteSingle',
        value: function onExecuteSingle(i) {
            console_log(this.name + ': ' + (i + 1) + '/' + this.numIteration);
        }
    }]);

    return BaseBenchmark;
}();

var KerasJSBenchmark = function (_BaseBenchmark) {
    _inherits(KerasJSBenchmark, _BaseBenchmark);

    function KerasJSBenchmark(name, flagGPU) {
        _classCallCheck(this, KerasJSBenchmark);

        var _this3 = _possibleConstructorReturn(this, (KerasJSBenchmark.__proto__ || Object.getPrototypeOf(KerasJSBenchmark)).call(this, name));

        _this3.model = null;
        _this3.flagGPU = flagGPU;
        _this3.xs = {
            'input_1': new Float32Array(224 * 224 * 3)
        };
        return _this3;
    }

    _createClass(KerasJSBenchmark, [{
        key: 'setupAsync',
        value: function setupAsync() {
            var prefix = './output/kerasjs/resnet50/model';
            this.model = new KerasJS.Model({
                filepaths: {
                    model: prefix + '.json',
                    weights: prefix + '_weights.buf',
                    metadata: prefix + '_metadata.json'
                },
                gpu: this.flagGPU
            });

            return this.model.ready();
        }
    }, {
        key: 'executeSingleAsync',
        value: function executeSingleAsync() {
            return this.model.predict(this.xs);
        }
    }, {
        key: 'finalizeAsync',
        value: function finalizeAsync() {
            this.model = null;
            this.xs = null;
        }
    }]);

    return KerasJSBenchmark;
}(BaseBenchmark);

var WebDNNBenchmark = function (_BaseBenchmark2) {
    _inherits(WebDNNBenchmark, _BaseBenchmark2);

    function WebDNNBenchmark(name, backend, flagOptimized) {
        _classCallCheck(this, WebDNNBenchmark);

        var _this4 = _possibleConstructorReturn(this, (WebDNNBenchmark.__proto__ || Object.getPrototypeOf(WebDNNBenchmark)).call(this, name));

        _this4.runner = null;
        _this4.x = null;
        _this4.y = null;
        _this4.backend = backend;
        _this4.flagOptimized = flagOptimized;
        return _this4;
    }

    _createClass(WebDNNBenchmark, [{
        key: 'setupAsync',
        value: function setupAsync() {
            var _this5 = this;

            //noinspection ES6ModulesDependencies
            return WebDNN.init([this.backend]).then(function () {
                //noinspection ES6ModulesDependencies
                _this5.runner = WebDNN.gpu.createDescriptorRunner();
                return _this5.runner.load('./output/webdnn/resnet50/' + (_this5.flagOptimized ? '' : 'non_') + 'optimized');
            }).then(function () {
                return _this5.runner.getInputViews();
            }).then(function (xs) {
                _this5.x = xs[0];
                return _this5.runner.getOutputViews();
            }).then(function (ys) {
                _this5.y = ys[0];
            });
        }
    }, {
        key: 'executeSingleAsync',
        value: function executeSingleAsync() {
            return this.runner.run();
        }
    }, {
        key: 'finalizeAsync',
        value: function finalizeAsync() {
            this.runner = null;
            this.x = null;
            this.y = null;
        }
    }]);

    return WebDNNBenchmark;
}(BaseBenchmark);

function run() {
    var numIteration = Number(document.forms.benchmark.iterations.value) + 1;
    if (isNaN(numIteration)) {
        numIteration = 5;
    }

    var mode_selection = document.forms.benchmark.mode_selection;
    var benchmark_id = 0;
    for (var i = 0; i < mode_selection.length; i++) {
        if (mode_selection[i].checked) {
            benchmark_id = Number(mode_selection[i].value);
        }
    }
    var benchmark = benchmarks[benchmark_id];

    var summaryHandler = function summaryHandler(summary) {
        return console_log(summary.name + ' : ' + summary.mean.toFixed(2) + '+-' + summary.std.toFixed(2) + 'ms');
    };

    console_log('Benchmark ' + benchmark.name + ' start');
    Promise.resolve().then(function () {
        return benchmark.runAsync(numIteration).then(summaryHandler);
    }).then(function () {
        return console_log('Benchmark end');
    }).catch(function (err) {
        return console_error(err);
    });
}

document.addEventListener('DOMContentLoaded', function (event) {
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebGPU) + Optimize', 'webgpu', true));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebGPU)', 'webgpu', false));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebAssembly) + Optimize', 'webassembly', true));
    benchmarks.push(new WebDNNBenchmark('WebDNN(WebAssembly)', 'webassembly', false));
    benchmarks.push(new KerasJSBenchmark('Keras.js(CPU)', false));
    benchmarks.push(new KerasJSBenchmark('Keras.js(GPU)', true));

    var div_modelist = document.getElementById('modelist');
    for (var i = 0; i < benchmarks.length; i++) {
        var benchmark = benchmarks[i];
        div_modelist.innerHTML += '<label><input type="radio" name="mode_selection" value="' + i + '" ' + (i == 0 ? 'checked' : '') + '>' + benchmark.name + '</label><br>';
    }

    var environment_note = "";
    if (typeof WebGPUComputeCommandEncoder === 'undefined') {
        environment_note += "This browser does not support WebGPU.\n";
    }
    if (typeof WebAssembly === 'undefined') {
        environment_note += "This browser does not support WebAssembly. WebAssembly backend will run in asm.js mode.\n";
    }
    document.getElementById('environment_note').innerHTML = environment_note;

    document.getElementById('run_button').disabled = false;
});
