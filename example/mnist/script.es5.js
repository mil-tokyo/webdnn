'use strict';

var onButtonClick = function () {
    var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
        return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
                switch (_context.prev = _context.next) {
                    case 0:
                        _context.prev = 0;
                        _context.next = 3;
                        return run();

                    case 3:
                        console.log('run finished');

                        _context.next = 10;
                        break;

                    case 6:
                        _context.prev = 6;
                        _context.t0 = _context['catch'](0);

                        showMessage('run failed: ' + _context.t0);
                        console.error('run failed ' + _context.t0);

                    case 10:
                    case 'end':
                        return _context.stop();
                }
            }
        }, _callee, this, [[0, 6]]);
    }));

    return function onButtonClick() {
        return _ref.apply(this, arguments);
    };
}();

var initialize = function () {
    var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
        var backend, framework;
        return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
                switch (_context2.prev = _context2.next) {
                    case 0:
                        backend = document.querySelector('input[name=backend]:checked').value;
                        framework = document.querySelector('input[name=framework]:checked').value;
                        _context2.next = 4;
                        return WebDNN.load('./output_' + framework, { backendOrder: backend });

                    case 4:
                        runner = _context2.sent;

                        showMessage('Backend: ' + runner.backendName + ', model converted from ' + framework);
                        console.info('Backend: ' + runner.backendName + ', model converted from ' + framework);
                        _context2.next = 9;
                        return fetchSamples('./output_' + framework + '/test_samples.json');

                    case 9:
                        samples = _context2.sent;

                        table = document.getElementById('result');

                    case 11:
                    case 'end':
                        return _context2.stop();
                }
            }
        }, _callee2, this);
    }));

    return function initialize() {
        return _ref2.apply(this, arguments);
    };
}();

var run = function () {
    var _ref3 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
        var totalElapsedTime, i, sample, start, predictedLabel;
        return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
                switch (_context3.prev = _context3.next) {
                    case 0:
                        if (runner) {
                            _context3.next = 3;
                            break;
                        }

                        _context3.next = 3;
                        return initialize();

                    case 3:
                        resetResult();

                        totalElapsedTime = 0;
                        i = 0;

                    case 6:
                        if (!(i < samples.length)) {
                            _context3.next = 21;
                            break;
                        }

                        sample = samples[i];

                        runner.inputs[0].set(sample.x);
                        console.log('ground truth: ' + sample.y);

                        start = performance.now();
                        _context3.next = 13;
                        return runner.run();

                    case 13:
                        totalElapsedTime += performance.now() - start;

                        console.log(runner.outputs[0]);

                        predictedLabel = WebDNN.Math.argmax(runner.outputs[0])[0];

                        console.log('predicted: ' + predictedLabel);

                        displayPrediction(sample.x, predictedLabel, sample.y);

                    case 18:
                        i++;
                        _context3.next = 6;
                        break;

                    case 21:

                        console.log('Elapsed Time [ms/image]: ' + (totalElapsedTime / samples.length).toFixed(2));

                    case 22:
                    case 'end':
                        return _context3.stop();
                }
            }
        }, _callee3, this);
    }));

    return function run() {
        return _ref3.apply(this, arguments);
    };
}();

var fetchSamples = function () {
    var _ref4 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4(path) {
        var response, json, samples, i;
        return regeneratorRuntime.wrap(function _callee4$(_context4) {
            while (1) {
                switch (_context4.prev = _context4.next) {
                    case 0:
                        _context4.next = 2;
                        return fetch(path);

                    case 2:
                        response = _context4.sent;

                        if (response.ok) {
                            _context4.next = 5;
                            break;
                        }

                        throw new Error('Failed to load test samples');

                    case 5:
                        _context4.next = 7;
                        return response.json();

                    case 7:
                        json = _context4.sent;
                        samples = [];

                        for (i = 0; i < json.length; i++) {
                            samples.push({ 'x': new Float32Array(json[i]['x']), 'y': json[i]['y'] });
                        }

                        return _context4.abrupt('return', samples);

                    case 11:
                    case 'end':
                        return _context4.stop();
                }
            }
        }, _callee4, this);
    }));

    return function fetchSamples(_x) {
        return _ref4.apply(this, arguments);
    };
}();

function _asyncToGenerator(fn) { return function () { var gen = fn.apply(this, arguments); return new Promise(function (resolve, reject) { function step(key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { return Promise.resolve(value).then(function (value) { step("next", value); }, function (err) { step("throw", err); }); } } return step("next"); }); }; }

var runner = null;
var samples = null;
var table = null;

function showMessage(text) {
    document.getElementById('message').textContent = text;
}

function reset() {
    runner = null;
    resetResult();
}

function resetResult() {
    if (!table) return;
    while (table.rows.length >= 2) {
        table.deleteRow(-1);
    }
}

function displayPrediction(inputImage, prediction, groundTruth) {
    var canvas = document.createElement('canvas');
    canvas.width = 28;
    canvas.height = 28;
    var ctx = canvas.getContext('2d');
    var img = ctx.createImageData(28, 28);
    for (var i = 0; i < 28 * 28; i++) {
        var pixel = inputImage[i] * 255;
        img.data[i * 4 + 0] = pixel; //r
        img.data[i * 4 + 1] = pixel; //g
        img.data[i * 4 + 2] = pixel; //b
        img.data[i * 4 + 3] = 255; //a
    }
    ctx.putImageData(img, 0, 0);

    var tr = table.insertRow();
    tr.appendChild(document.createElement('td')).appendChild(canvas);
    tr.appendChild(document.createElement('td')).textContent = '' + prediction;
    tr.appendChild(document.createElement('td')).textContent = '' + groundTruth;
}
