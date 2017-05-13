'use strict';

let $M, $Mg;
let runner;

function run_entry() {
    run().catch(err => console.error(err));
}

async function run() {
    if (!$M) {
        await init();
    }

    let pipeline_data = JSON.parse((document.getElementById('dnn_pipeline')).value);
    runner = $M.gpu.createDescriptorRunner(pipeline_data);
    await runner.compile();

    await runner.loadWeights(await fetchWeights('./output/weight.bin'));

    let input_views = await runner.getInputViews();
    let output_views = await runner.getOutputViews();
    let input_mat = new Float32Array([1.0, 1.0, -1.0]);
    input_views[0].set(input_mat);
    await runner.run([input_mat]);
    console.log(output_views[0]);
}

async function init() {
    $M = WebDNN;
    let backend = await $M.init($('input[name=backend_name]:checked').val());
    console.log(`backend: ${backend}`);
    $Mg = $M.gpu;
}

async function fetchWeights(path) {
    let response = await fetch(path);
    let ab = await response.arrayBuffer();

    return new Uint8Array(ab);
}
