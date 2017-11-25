// compile in https://babeljs.io/repl/#?babili=false&browsers=&build=&builtIns=false

'use strict';

var run_entry = function () {
    var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
        return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
                switch (_context.prev = _context.next) {
                    case 0:
                        _context.prev = 0;
                        _context.next = 3;
                        return run();

                    case 3:
                        log('Run finished');

                        _context.next = 9;
                        break;

                    case 6:
                        _context.prev = 6;
                        _context.t0 = _context['catch'](0);

                        log('Error: ' + _context.t0);

                    case 9:
                    case 'end':
                        return _context.stop();
                }
            }
        }, _callee, this, [[0, 6]]);
    }));

    return function run_entry() {
        return _ref.apply(this, arguments);
    };
}();

var loadImage = function () {
    var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
        var imageData;
        return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
                switch (_context2.prev = _context2.next) {
                    case 0:
                        _context2.next = 2;
                        return WebDNN.Image.getImageArray(document.getElementById("image_url").value, { dstW: 224, dstH: 224 });

                    case 2:
                        imageData = _context2.sent;

                        WebDNN.Image.setImageArrayToCanvas(imageData, 224, 224, document.getElementById('input_image'));

                        document.getElementById('run_button').disabled = false;
                        log('Image loaded to canvas');

                    case 6:
                    case 'end':
                        return _context2.stop();
                }
            }
        }, _callee2, this);
    }));

    return function loadImage() {
        return _ref2.apply(this, arguments);
    };
}();

var prepare_run = function () {
    var _ref3 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
        var backend_name, framework_name, backend_key, runner;
        return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
                switch (_context3.prev = _context3.next) {
                    case 0:
                        backend_name = document.querySelector('input[name=backend]:checked').value;
                        framework_name = getFrameworkName();
                        backend_key = backend_name + framework_name;

                        if (backend_key in runners) {
                            _context3.next = 12;
                            break;
                        }

                        log('Initializing and loading model');
                        _context3.next = 7;
                        return WebDNN.load('./output_' + framework_name, { backendOrder: backend_name });

                    case 7:
                        runner = _context3.sent;

                        log('Loaded backend: ' + runner.backendName + ', model converted from ' + framework_name);

                        runners[backend_key] = runner;
                        _context3.next = 13;
                        break;

                    case 12:
                        log('Model is already loaded');

                    case 13:
                        return _context3.abrupt('return', runners[backend_key]);

                    case 14:
                    case 'end':
                        return _context3.stop();
                }
            }
        }, _callee3, this);
    }));

    return function prepare_run() {
        return _ref3.apply(this, arguments);
    };
}();

var run = function () {
    var _ref4 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4() {
        var runner, start, elapsed_time, out_vec, top_labels, predicted_str, j;
        return regeneratorRuntime.wrap(function _callee4$(_context4) {
            while (1) {
                switch (_context4.prev = _context4.next) {
                    case 0:
                        _context4.next = 2;
                        return prepare_run();

                    case 2:
                        runner = _context4.sent;
                        _context4.t0 = runner.getInputViews()[0];
                        _context4.next = 6;
                        return WebDNN.Image.getImageArray(document.getElementById('input_image'), {
                            order: getFrameworkName() === 'chainer' ? WebDNN.Image.Order.CHW : WebDNN.Image.Order.HWC,
                            color: WebDNN.Image.Color.BGR,
                            bias: [123.68, 116.779, 103.939]
                        });

                    case 6:
                        _context4.t1 = _context4.sent;

                        _context4.t0.set.call(_context4.t0, _context4.t1);

                        start = performance.now();
                        _context4.next = 11;
                        return runner.run();

                    case 11:
                        elapsed_time = performance.now() - start;
                        out_vec = runner.getOutputViews()[0].toActual();
                        top_labels = WebDNN.Math.argmax(out_vec, 5);
                        predicted_str = 'Predicted:';

                        for (j = 0; j < top_labels.length; j++) {
                            predicted_str += ' ' + top_labels[j] + '(' + imagenet_labels[top_labels[j]] + ')';
                        }
                        log(predicted_str);

                        console.log('output vector: ', out_vec);
                        log('Total Elapsed Time[ms/image]: ' + elapsed_time.toFixed(2));

                    case 19:
                    case 'end':
                        return _context4.stop();
                }
            }
        }, _callee4, this);
    }));

    return function run() {
        return _ref4.apply(this, arguments);
    };
}();

function _asyncToGenerator(fn) { return function () { var gen = fn.apply(this, arguments); return new Promise(function (resolve, reject) { function step(key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { return Promise.resolve(value).then(function (value) { step("next", value); }, function (err) { step("throw", err); }); } } return step("next"); }); }; }

function log(msg) {
    var msg_node = document.getElementById('messages');
    msg_node.appendChild(document.createElement('br'));
    msg_node.appendChild(document.createTextNode(msg));
}

var runners = {};

function getFrameworkName() {
    return document.querySelector('input[name=framework]:checked').value;
}
