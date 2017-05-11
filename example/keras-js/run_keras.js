'use strict';
// ES5 (with Promise polyfill)

var model;
var image_size = 224;
var image_data;

function msg(s) {
    document.getElementById('msg_placeholder').textContent = s;
}

function do_setup() {
    msg('loading model');

    var model_prefix = './data/resnet50';
    model = new KerasJS.Model({
        filepaths: {
            model: model_prefix + '.json',
            weights: model_prefix + '_weights.buf',
            metadata: model_prefix + '_metadata.json'
        },
        gpu: document.forms.bench_setting.gpu.checked
    });

    model.ready().then(function () {
        msg('Model ready');
        document.forms.bench_setting.setup.disabled = true;
        document.forms.bench_setting.inference.disabled = false;
    }).catch(function (reason) {
        msg('Loading error: ' + reason);
    });
}

function do_inference() {
    var inputData = {
        'input_1': image_data
    };

    msg('Performing inference...');
    var start_t = performance.now();
    model.predict(inputData).then(function (outputData) {
        var end_t = performance.now();
        // outputData['fc1000'] contains result
        var scores = outputData['fc1000'];
        var max_score = -Infinity;
        var max_label = 0;
        for (var i = 0; i < scores.length; i++) {
            if (scores[i] > max_score) {
                max_score = scores[i];
                max_label = i;
            }
        }
        msg('Predicted label=' + max_label + ', finished in ' + (end_t - start_t).toFixed(0) + ' ms');
    }).catch(function (reason) {
        msg('Inference error: ' + reason);
    });
}

function do_load_image() {
    loadImage().then(function () {
        msg('Image for inference is loaded');
    }).catch(function (reason) {
        msg('Image cannot be loaded');
    });
}

function loadImage() {
    return new Promise(function (resolve, reject) {
        var img = new Image();
        img.onload = function () {
            var ctx = document.getElementById('input_image').getContext('2d');
            // shrink instead of crop
            ctx.drawImage(img, 0, 0, image_size, image_size);

            image_data = getImageData(ctx);
            resolve();
        }
        img.onerror = reject;
        img.src = document.forms.bench_setting.image_url.value;
    });
}

function getImageData(ctx) {
    let h = image_size;
    let w = image_size;
    let imagedata = ctx.getImageData(0, 0, h, w);//h,w,c(rgba)
    let pixeldata = imagedata.data;
    let data = new Float32Array(3 * h * w);//h,w,c(bgr)
    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            data[(y * w + x) * 3] = pixeldata[(y * w + x) * 4 + 2] - 103.939;//b
            data[(y * w + x) * 3 + 1] = pixeldata[(y * w + x) * 4 + 1] - 116.779;//g
            data[(y * w + x) * 3 + 2] = pixeldata[(y * w + x) * 4 + 0] - 123.68;//r
        }
    }
    return data;
}
