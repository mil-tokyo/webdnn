'use strict';

var $M, $Mg;
var runner;
var is_image_loaded = false;
var image_size = 227;

function run_entry() {
    run().then(() => {
        console.log('run finished');
    }).catch((error) => {
        console.error('run failed ' + error);
    });
}

function load_image() {
    var img = new Image();
    img.onload = function () {
        var ctx = $('#input_image')[0].getContext('2d');
        // shrink instead of crop
        ctx.drawImage(img, 0, 0, image_size, image_size);
        is_image_loaded = true;
        $('#mini_msg').text('Image loaded to canvas');
    }
    img.src = $("input[name=image_url]").val();
}

let flag_prepared = false;
let test_samples;

async function prepare_run() {
    if (flag_prepared) return;

    let backend_name = $('input[name=backend_name]:checked').val();
    if (!$M) {
        backend_name = await init(backend_name);
    }

    runner = $M.gpu.createDNNDescriptorRunner();
    runner.ignoreCache = true;
    await runner.load('./output');

    let test_image;
    if (is_image_loaded) {
        test_image = getImageData();
    } else {
        test_image = await fetchImage('./output/image_nhwc.json');
    }
    test_samples = [test_image];

    flag_prepared = true;
}

async function run() {
    await prepare_run();

    let input_views = await runner.getInputViews();
    let output_views = await runner.getOutputViews();

    let total_elapsed_time = 0;
    let pred_label;
    for (let i = 0; i < test_samples.length; i++) {
        let sample = test_samples[i];
        input_views[0].set(sample);

        let start = performance.now();
        await runner.run();
        total_elapsed_time += performance.now() - start;

        let out_vec = output_views[0];
        pred_label = 0;
        let pred_score = -Infinity;
        for (let j = 0; j < out_vec.length; j++) {
            if (out_vec[j] > pred_score) {
                pred_score = out_vec[j];
                pred_label = j;
            }
        }
        console.log(`predicted: ${pred_label}`);
        console.log(out_vec);
    }
    console.log(`Total Elapsed Time[ms/image]: ${(total_elapsed_time / test_samples.length).toFixed(2)}`);
    $('#mini_msg').text(`Total Elapsed Time[ms/image]: ${(total_elapsed_time / test_samples.length).toFixed(2)}, label=${pred_label}`);
}

async function init(backend_name) {
    $M = WebDNN;
    let backend = await $M.init(backend_name);
    console.log(`backend: ${backend}`);
    $Mg = $M.gpu;
    return backend;
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
