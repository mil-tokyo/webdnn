'use strict';

var prepare_run = function () {
    var _ref = _asyncToGenerator(regeneratorRuntime.mark(function _callee() {
        var backend_name, test_image;
        return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
                switch (_context.prev = _context.next) {
                    case 0:
                        if (!flag_prepared) {
                            _context.next = 2;
                            break;
                        }

                        return _context.abrupt('return');

                    case 2:
                        backend_name = $('input[name=backend_name]:checked').val();

                        if ($M) {
                            _context.next = 7;
                            break;
                        }

                        _context.next = 6;
                        return init(backend_name);

                    case 6:
                        backend_name = _context.sent;

                    case 7:

                        runner = $M.gpu.createDescriptorRunner();
                        runner.ignoreCache = true;
                        _context.next = 11;
                        return runner.load('./output');

                    case 11:
                        test_image = void 0;

                        if (!is_image_loaded) {
                            _context.next = 16;
                            break;
                        }

                        test_image = getImageData();
                        _context.next = 19;
                        break;

                    case 16:
                        _context.next = 18;
                        return fetchImage('./output/image_nhwc.json');

                    case 18:
                        test_image = _context.sent;

                    case 19:
                        test_samples = [test_image];

                        flag_prepared = true;

                    case 21:
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

var run = function () {
    var _ref2 = _asyncToGenerator(regeneratorRuntime.mark(function _callee2() {
        var input_views, output_views, total_elapsed_time, pred_label, i, sample, start, out_vec, pred_score, j;
        return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
                switch (_context2.prev = _context2.next) {
                    case 0:
                        _context2.next = 2;
                        return prepare_run();

                    case 2:
                        _context2.next = 4;
                        return runner.getInputViews();

                    case 4:
                        input_views = _context2.sent;
                        _context2.next = 7;
                        return runner.getOutputViews();

                    case 7:
                        output_views = _context2.sent;
                        total_elapsed_time = 0;
                        pred_label = void 0;
                        i = 0;

                    case 11:
                        if (!(i < test_samples.length)) {
                            _context2.next = 27;
                            break;
                        }

                        sample = test_samples[i];

                        input_views[0].set(sample);

                        start = performance.now();
                        _context2.next = 17;
                        return runner.run();

                    case 17:
                        total_elapsed_time += performance.now() - start;

                        out_vec = output_views[0];

                        pred_label = 0;
                        pred_score = -Infinity;

                        for (j = 0; j < out_vec.length; j++) {
                            if (out_vec[j] > pred_score) {
                                pred_score = out_vec[j];
                                pred_label = j;
                            }
                        }
                        console.log('predicted: ' + pred_label);
                        console.log(out_vec);

                    case 24:
                        i++;
                        _context2.next = 11;
                        break;

                    case 27:
                        console.log('Total Elapsed Time[ms/image]: ' + (total_elapsed_time / test_samples.length).toFixed(2));
                        $('#mini_msg').text('Total Elapsed Time[ms/image]: ' + (total_elapsed_time / test_samples.length).toFixed(2) + ', label=' + pred_label);

                    case 29:
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

var init = function () {
    var _ref3 = _asyncToGenerator(regeneratorRuntime.mark(function _callee3(backend_name) {
        var backend;
        return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
                switch (_context3.prev = _context3.next) {
                    case 0:
                        $M = WebDNN;
                        _context3.next = 3;
                        return $M.init(backend_name);

                    case 3:
                        backend = _context3.sent;

                        console.log('backend: ' + backend);
                        $Mg = $M.gpu;
                        return _context3.abrupt('return', backend);

                    case 7:
                    case 'end':
                        return _context3.stop();
                }
            }
        }, _callee3, this);
    }));

    return function init(_x) {
        return _ref3.apply(this, arguments);
    };
}();

var fetchImage = function () {
    var _ref4 = _asyncToGenerator(regeneratorRuntime.mark(function _callee4(path) {
        var response, json;
        return regeneratorRuntime.wrap(function _callee4$(_context4) {
            while (1) {
                switch (_context4.prev = _context4.next) {
                    case 0:
                        _context4.next = 2;
                        return fetch(path);

                    case 2:
                        response = _context4.sent;
                        _context4.next = 5;
                        return response.json();

                    case 5:
                        json = _context4.sent;
                        return _context4.abrupt('return', new Float32Array(json));

                    case 7:
                    case 'end':
                        return _context4.stop();
                }
            }
        }, _callee4, this);
    }));

    return function fetchImage(_x2) {
        return _ref4.apply(this, arguments);
    };
}();

function _asyncToGenerator(fn) { return function () { var gen = fn.apply(this, arguments); return new Promise(function (resolve, reject) { function step(key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { return Promise.resolve(value).then(function (value) { step("next", value); }, function (err) { step("throw", err); }); } } return step("next"); }); }; }

var $M, $Mg;
var runner;
var is_image_loaded = false;

function run_entry() {
    run().then(function () {
        console.log('run finished');
    }).catch(function (error) {
        console.error('run failed ' + error);
    });
}

function load_image() {
    var img = new Image();
    img.onload = function () {
        var ctx = $('#input_image')[0].getContext('2d');
        // shrink instead of crop
        ctx.drawImage(img, 0, 0, 224, 224);
        is_image_loaded = true;
        $('#mini_msg').text('Image loaded to canvas');
    };
    img.src = $("input[name=image_url]").val();
}

var flag_prepared = false;
var test_samples = void 0;

function makeMatFromJson(mat_data) {
    var mat = new Float32Array(mat_data['data']);
    return mat;
}

function getImageData() {
    var ctx = $('#input_image')[0].getContext('2d');
    var h = 224;
    var w = 224;
    var imagedata = ctx.getImageData(0, 0, h, w); //h,w,c(rgba)
    var pixeldata = imagedata.data;
    var data = new Float32Array(3 * h * w); //h,w,c(bgr)
    for (var y = 0; y < h; y++) {
        for (var x = 0; x < w; x++) {
            data[(y * w + x) * 3] = pixeldata[(y * w + x) * 4 + 2] - 103.939; //b
            data[(y * w + x) * 3 + 1] = pixeldata[(y * w + x) * 4 + 1] - 116.779; //g
            data[(y * w + x) * 3 + 2] = pixeldata[(y * w + x) * 4 + 0] - 123.68; //r
        }
    }
    return data;
}
