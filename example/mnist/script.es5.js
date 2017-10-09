'use strict';

var run = function () {
    var _ref = _asyncToGenerator(regeneratorRuntime.mark(function _callee() {
        var backend_name, framework_name, output_table, total_elapsed_time, i, sample, start, out_vec, pred_label;
        return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
                switch (_context.prev = _context.next) {
                    case 0:
                        if (runner) {
                            _context.next = 11;
                            break;
                        }

                        backend_name = document.querySelector('input[name=backend_name]:checked').value;
                        framework_name = document.querySelector('input[name=framework_name]:checked').value;
                        _context.next = 5;
                        return WebDNN.load('./output_' + framework_name, { backendOrder: backend_name });

                    case 5:
                        runner = _context.sent;

                        msg('Backend: ' + runner.backendName + ', model converted from ' + framework_name);
                        console.info('Backend: ' + runner.backendName + ', model converted from ' + framework_name);
                        _context.next = 10;
                        return fetchSamples('./output_' + framework_name + '/test_samples.json');

                    case 10:
                        test_samples = _context.sent;

                    case 11:
                        output_table = document.getElementById('result');

                        resetOutputTable(output_table);

                        total_elapsed_time = 0;
                        i = 0;

                    case 15:
                        if (!(i < test_samples.length)) {
                            _context.next = 31;
                            break;
                        }

                        sample = test_samples[i];

                        runner.getInputViews()[0].set(sample.x);
                        console.log('ground truth: ' + sample.y);

                        start = performance.now();
                        _context.next = 22;
                        return runner.run();

                    case 22:
                        total_elapsed_time += performance.now() - start;

                        out_vec = runner.getOutputViews()[0].toActual();
                        pred_label = WebDNN.Math.argmax(out_vec)[0];

                        console.log('predicted: ' + pred_label);
                        console.log(out_vec);
                        displayPrediction(output_table, sample.x, pred_label, sample.y);

                    case 28:
                        i++;
                        _context.next = 15;
                        break;

                    case 31:
                        console.log('Total Elapsed Time[ms/image]: ' + (total_elapsed_time / test_samples.length).toFixed(2));

                    case 32:
                    case 'end':
                        return _context.stop();
                }
            }
        }, _callee, this);
    }));

    return function run() {
        return _ref.apply(this, arguments);
    };
}();

var fetchSamples = function () {
    var _ref2 = _asyncToGenerator(regeneratorRuntime.mark(function _callee2(path) {
        var response, json, samples, i;
        return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
                switch (_context2.prev = _context2.next) {
                    case 0:
                        _context2.next = 2;
                        return webdnnFetch(path);

                    case 2:
                        response = _context2.sent;

                        if (response.ok) {
                            _context2.next = 5;
                            break;
                        }

                        throw new Error('Failed to load test samples');

                    case 5:
                        _context2.next = 7;
                        return response.json();

                    case 7:
                        json = _context2.sent;
                        samples = [];

                        for (i = 0; i < json.length; i++) {
                            samples.push({ 'x': new Float32Array(json[i]['x']), 'y': json[i]['y'] });
                        }

                        return _context2.abrupt('return', samples);

                    case 11:
                    case 'end':
                        return _context2.stop();
                }
            }
        }, _callee2, this);
    }));

    return function fetchSamples(_x) {
        return _ref2.apply(this, arguments);
    };
}();

function _asyncToGenerator(fn) { return function () { var gen = fn.apply(this, arguments); return new Promise(function (resolve, reject) { function step(key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { return Promise.resolve(value).then(function (value) { step("next", value); }, function (err) { step("throw", err); }); } } return step("next"); }); }; }

var runner = null;
var test_samples = null;

function msg(s) {
    document.getElementById('msg_place').textContent = s;
}

function run_entry() {
    run().then(function () {
        console.log('run finished');
    }).catch(function (error) {
        msg('run failed: ' + error);
        console.error('run failed ' + error);
    });
}

function reset_backend() {
    runner = null;
    resetOutputTable(document.getElementById('result'));
    msg('Resetted backend');
}

function resetOutputTable(table) {
    var rows = table.children;
    for (var i = rows.length - 1; i >= 1; i--) {
        table.removeChild(rows[i]);
    }
}

function displayPrediction(table, input_image, prediction, ground_truth) {
    var tr = document.createElement('tr');
    var canvas = document.createElement('canvas');
    canvas.width = 28;
    canvas.height = 28;
    var ctx = canvas.getContext('2d');
    var img = ctx.createImageData(28, 28);
    for (var i = 0; i < 28 * 28; i++) {
        var pixel = input_image[i] * 255;
        img.data[i * 4 + 0] = pixel; //r
        img.data[i * 4 + 1] = pixel; //g
        img.data[i * 4 + 2] = pixel; //b
        img.data[i * 4 + 3] = 255; //a
    }
    ctx.putImageData(img, 0, 0);
    tr.appendChild(document.createElement('td')).appendChild(canvas);
    tr.appendChild(document.createElement('td')).textContent = '' + prediction;
    tr.appendChild(document.createElement('td')).textContent = '' + ground_truth;

    table.appendChild(tr);
}
