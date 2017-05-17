'use strict';

var is_image_loaded = false;
var image_size = 227;

function run_entry() {
    run().then(() => {
        log('Run finished');
    }).catch((error) => {
        log('Error: ' + error);
    });
}

function log(msg) {
    $('#messages').append('<br>').append(document.createTextNode(msg));
}

function load_image() {
    var img = new Image();
    img.onload = function () {
        var ctx = $('#input_image')[0].getContext('2d');
        // shrink instead of crop
        ctx.drawImage(img, 0, 0, image_size, image_size);
        is_image_loaded = true;
        $('#run_button').prop('disabled', false);
        log('Image loaded to canvas');
    }
    img.onerror = function () {
        log('Failed to load image');
    }
    img.src = $("input[name=image_url]").val();
}

let run_if = null;

async function prepare_run() {
    if (run_if) {
        return;
    }
    let backend_name = $('input[name=backend_name]:checked').val();
    log('Initializing and loading model');
    run_if = await WebDNN.prepareAll('./output', { backendOrder: backend_name });
    log(`Loaded backend: ${run_if.backendName}`);
}

async function run() {
    await prepare_run();

    let total_elapsed_time = 0;
    let pred_label;
    let test_image = getImageData();
    let test_samples = [test_image];

    log('Running model...');
    for (let i = 0; i < test_samples.length; i++) {
        let sample = test_samples[i];
        run_if.inputViews[0].set(sample);

        let start = performance.now();
        await run_if.run();
        total_elapsed_time += performance.now() - start;

        let out_vec = run_if.outputViews[0];
        let top_labels = WebDNN.Math.argmax(out_vec, 5);
        let predicted_str = 'Predicted:';
        for (let j = 0; j < top_labels.length; j++) {
            predicted_str += ` ${top_labels[j]}(${imagenet_labels[top_labels[j]]})`;
        }
        log(predicted_str);
        console.log('output vector: ', out_vec);
    }
    log(`Total Elapsed Time[ms/image]: ${(total_elapsed_time / test_samples.length).toFixed(2)}, backend=${run_if.backendName}`);
}

function makeMatFromJson(mat_data) {
    var mat = new Float32Array(mat_data['data']);
    return mat;
}

async function fetchImage(path) {
    let response = await fetch(path);
    let json = await response.json();

    return new Float32Array(json);
}

function getImageData() {
    let ctx = $('#input_image')[0].getContext('2d');
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
