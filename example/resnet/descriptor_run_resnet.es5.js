'use strict';

var prepare_run = function() {
    var _ref = _asyncToGenerator(regeneratorRuntime.mark(function _callee() {
        var backend_name, framework_name, backend_key, runner;
        return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
                switch (_context.prev = _context.next) {
                    case 0:
                        backend_name = document.querySelector('input[name=backend_name]:checked').value;
                        framework_name = getFrameworkName();
                        backend_key = backend_name + framework_name;

                        if (backend_key in runners) {
                            _context.next = 12;
                            break;
                        }

                        log('Initializing and loading model');
                        _context.next = 7;
                        return WebDNN.load('./output_' + framework_name, {backendOrder: backend_name});

                    case 7:
                        runner = _context.sent;

                        log('Loaded backend: ' + runner.backendName + ', model converted from ' + framework_name);

                        runners[backend_key] = runner;
                        _context.next = 13;
                        break;

                    case 12:
                        log('Model is already loaded');

                    case 13:
                        return _context.abrupt('return', runners[backend_key]);

                    case 14:
                    case 'end':
                        return _context.stop();
                }
            }
        }, _callee, this);
    }));

    return function prepare_run() {
        return _ref.apply(this, arguments);
    };
}();

var run = function() {
    var _ref2 = _asyncToGenerator(regeneratorRuntime.mark(function _callee2() {
        var runner, test_image, test_samples, total_elapsed_time, pred_label, i, sample, start, out_vec, top_labels, predicted_str, j;
        return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
                switch (_context2.prev = _context2.next) {
                    case 0:
                        _context2.next = 2;
                        return prepare_run();

                    case 2:
                        runner = _context2.sent;
                        test_image = getImageData(getFrameworkName() === 'chainer');
                        test_samples = [test_image];
                        total_elapsed_time = 0;
                        pred_label = void 0;
                        i = 0;

                    case 8:
                        if (!(i < test_samples.length)) {
                            _context2.next = 24;
                            break;
                        }

                        sample = test_samples[i];

                        runner.getInputViews()[0].set(sample);

                        start = performance.now();
                        _context2.next = 14;
                        return runner.run();

                    case 14:
                        total_elapsed_time += performance.now() - start;

                        out_vec = runner.getOutputViews()[0].toActual();
                        top_labels = WebDNN.Math.argmax(out_vec, 5);
                        predicted_str = 'Predicted:';

                        for (j = 0; j < top_labels.length; j++) {
                            predicted_str += ' ' + top_labels[j] + '(' + imagenet_labels[top_labels[j]] + ')';
                        }
                        log(predicted_str);
                        console.log('output vector: ', out_vec);

                    case 21:
                        i++;
                        _context2.next = 8;
                        break;

                    case 24:
                        log('Total Elapsed Time[ms/image]: ' + (total_elapsed_time / test_samples.length).toFixed(2));

                    case 25:
                    case 'end':
                        return _context2.stop();
                }
            }
        }, _callee2, this);
    }));

    return function run() {
        return _ref2.apply(this, arguments);
    };
}();

function _asyncToGenerator(fn) {
    return function() {
        var gen = fn.apply(this, arguments);
        return new Promise(function(resolve, reject) {
            function step(key, arg) {
                try {
                    var info = gen[key](arg);
                    var value = info.value;
                } catch (error) {
                    reject(error);
                    return;
                }
                if (info.done) {
                    resolve(value);
                } else {
                    return Promise.resolve(value).then(function(value) {
                        step("next", value);
                    }, function(err) {
                        step("throw", err);
                    });
                }
            }

            return step("next");
        });
    };
}

var is_image_loaded = false;

function getFrameworkName() {
    return document.querySelector('input[name=framework_name]:checked').value;
}

function run_entry() {
    run().then(function() {
        log('Run finished');
    }).catch(function(error) {
        log('Error: ' + error);
    });
}

function log(msg) {
    var msg_node = document.getElementById('messages');
    msg_node.appendChild(document.createElement('br'));
    msg_node.appendChild(document.createTextNode(msg));
}

function load_image() {
    var img = new Image();
    img.onload = function() {
        var ctx = document.getElementById('input_image').getContext('2d');
        // shrink instead of crop
        ctx.drawImage(img, 0, 0, 224, 224);
        is_image_loaded = true;
        document.getElementById('run_button').disabled = false;
        log('Image loaded to canvas');
    };
    img.onerror = function() {
        log('Failed to load image');
    };
    img.src = document.querySelector("input[name=image_url]").value;
}

var runners = {};

function getImageData(flagNCHW) {
    var ctx = document.getElementById('input_image').getContext('2d');
    var h = 224;
    var w = 224;
    var imagedata = ctx.getImageData(0, 0, h, w); //h,w,c(rgba)
    var pixeldata = imagedata.data;
    var data = new Float32Array(3 * h * w); //h,w,c(bgr)

    if (flagNCHW) {
        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                data[(0 * h + y) * w + x] = pixeldata[(y * w + x) * 4 + 2] - 103.939;//b
                data[(1 * h + y) * w + x] = pixeldata[(y * w + x) * 4 + 1] - 116.779;//g
                data[(2 * h + y) * w + x] = pixeldata[(y * w + x) * 4 + 0] - 123.68;//r
            }
        }
    } else {
        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                data[(y * w + x) * 3] = pixeldata[(y * w + x) * 4 + 2] - 103.939;//b
                data[(y * w + x) * 3 + 1] = pixeldata[(y * w + x) * 4 + 1] - 116.779;//g
                data[(y * w + x) * 3 + 2] = pixeldata[(y * w + x) * 4 + 0] - 123.68;//r
            }
        }
    }
    return data;
}
