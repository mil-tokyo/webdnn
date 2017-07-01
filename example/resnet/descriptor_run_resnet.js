'use strict';

var is_image_loaded = false;

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
    img.onload = function() {
        var ctx = document.getElementById('input_image').getContext('2d');
        // shrink instead of crop
        ctx.drawImage(img, 0, 0, 224, 224);
        is_image_loaded = true;
        document.getElementById('run_button').disabled = false;
        log('Image loaded to canvas');
    }
    img.onerror = function() {
        log('Failed to load image');
    }
    img.src = document.querySelector("input[name=image_url]").value;
}

let test_samples;
let runners = {};

async function prepare_run() {
    let backend_name = document.querySelector('input[name=backend_name]:checked').value;
    let framework_name = document.querySelector('input[name=framework_name]:checked').value;
    let backend_key = backend_name + framework_name;
    if (!(backend_key in runners)) {
        log('Initializing and loading model');
        let runner = await WebDNN.load(`./output_${framework_name}`, {backendOrder: backend_name});
        log(`Loaded backend: ${runner.backendName}, model converted from ${framework_name}`);

        runners[backend_key] = runner;
    } else {
        log('Model is already loaded');
    }
    return runners[backend_key];
}

async function run() {
    let runner = await prepare_run();

    let test_image = getImageData();
    let test_samples = [test_image];

    let total_elapsed_time = 0;
    let pred_label;
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
    log(`Total Elapsed Time[ms/image]: ${(total_elapsed_time / test_samples.length).toFixed(2)}`);
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
    let ctx = document.getElementById('input_image').getContext('2d');
    let h = 224;
    let w = 224;
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
