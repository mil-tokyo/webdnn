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
    let msg_node = document.getElementById('messages');
    msg_node.appendChild(document.createElement('br'));
    msg_node.appendChild(document.createTextNode(msg));
}

function load_image() {
    var img = new Image();
    img.onload = function () {
        var ctx = document.getElementById('input_image').getContext('2d');
        // shrink instead of crop
        ctx.drawImage(img, 0, 0, image_size, image_size);
        is_image_loaded = true;
        document.getElementById('run_button').disabled = false;
        log('Image loaded to canvas');
    }
    img.onerror = function () {
        log('Failed to load image');
    }
    img.src = document.querySelector("input[name=image_url]").value;
}

let runners = {};

async function prepare_run() {
    let backend_name = document.querySelector('input[name=backend_name]:checked').value;
    if (!(backend_name in runners)) {
        log('Initializing and loading model');
        let runner = await WebDNN.load('./output', { backendOrder: backend_name });
        log(`Loaded backend: ${runner.backendName}`);

        runners[backend_name] = runner;
    } else {
        log('Model is already loaded');
    }
    return runners[backend_name];
}

async function run() {
    let runner = await prepare_run();

    let total_elapsed_time = 0;
    let pred_label;
    let test_image = getImageData();
    let test_samples = [test_image];

    log('Running model...');
    for (let i = 0; i < test_samples.length; i++) {
        let sample = test_samples[i];
        runner.getInputViews()[0].set(sample);

        let start = performance.now();
        await runner.run();
        total_elapsed_time += performance.now() - start;

        let out_vec = runner.getOutputViews()[0].toActual();
        let top_labels = WebDNN.Math.argmax(out_vec, 5);
        let predicted_str = 'Predicted:';
        for (let j = 0; j < top_labels.length; j++) {
            predicted_str += ` ${top_labels[j]}(${imagenet_labels[top_labels[j]]})`;
        }
        log(predicted_str);
        console.log('output vector: ', out_vec);
    }
    log(`Total Elapsed Time[ms/image]: ${(total_elapsed_time / test_samples.length).toFixed(2)}, backend=${runner.backendName}`);
}

function makeMatFromJson(mat_data) {
    var mat = new Float32Array(mat_data['data']);
    return mat;
}

async function fetchImage(path) {
    let response = await webdnnFetch(path);
    let json = await response.json();

    return new Float32Array(json);
}

function getImageData() {
    let ctx = document.getElementById('input_image').getContext('2d');
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
