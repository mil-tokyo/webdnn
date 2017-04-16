'use strict';

var $M, $Mg;
var runner;

function run_entry() {
    run().then(() => {
        console.log('run finished');
    }).catch((error) => {
        console.error('run failed ' + error);
    });
}

async function run() {
    let backend_name = $('input[name=backend_name]:checked').val();
    if (!$M) {
        backend_name = await init(backend_name);
    }

    let pipeline_data = JSON.parse($('#dnn_pipeline').val());
    runner = $M.gpu.createDNNDescriptorRunner(pipeline_data);
    await runner.compile();

    await runner.loadWeights(await fetchWeights('./output/weight_' + backend_name + '.bin'));
    let test_samples = await fetchSamples('../../resources/mnist/test_samples.json');
    let input_views = await runner.getInputViews();
    let output_views = await runner.getOutputViews();

    for (let i = 0; i < test_samples.length; i++) {
        let sample = test_samples[i];
        input_views[0].set(sample.x);
        console.log(`ground truth: ${sample.y}`);
        await runner.run();

        let out_vec = output_views[0];
        let pred_label = 0;
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
}

async function init(backend_name) {
    $M = WebDNN;
    let backend = await $M.init(backend_name);
    console.log(`backend: ${backend}`);
    $Mg = $M.gpu;
    return backend;
}

async function fetchWeights(path) {
    let response = await fetch(path);
    let ab = await response.arrayBuffer();
    let weights_data = new Float32Array(ab);

    return weights_data;
}

function makeMatFromJson(mat_data) {
    var mat = new Float32Array(mat_data['data']);
    return mat;
}

async function fetchSamples(path) {
    let response = await fetch(path);
    let json = await response.json();
    let samples = [];
    for (let i = 0; i < json.length; i++) {
        samples.push({ 'x': makeMatFromJson(json[i]['x']), 'y': json[i]['y'] });
    }

    return samples;
}
