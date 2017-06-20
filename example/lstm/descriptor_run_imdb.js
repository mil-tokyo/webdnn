'use strict';

let run_if = null;
let test_samples = null;

function msg(s) {
    document.getElementById('msg_place').textContent = s;
}

function run_entry() {
    run().then(() => {
        console.log('run finished');
    }).catch((error) => {
        msg('run failed: ' + error);
        console.error('run failed ' + error);
    });
}

function reset_backend() {
    run_if = null;
    resetOutputTable(document.getElementById('result'));
    msg('Resetted backend');
}

async function run() {
    if (!run_if) {
        let backend_name = document.querySelector('input[name=backend_name]:checked').value;
        let framework_name = document.querySelector('input[name=framework_name]:checked').value;
        run_if = await WebDNN.prepareAll(`./output_${framework_name}`, { backendOrder: backend_name });
        msg(`Backend: ${run_if.backendName}, model converted from ${framework_name}`);
        console.info(`Backend: ${run_if.backendName}, model converted from ${framework_name}`);
        test_samples = await fetchSamples(`./output_${framework_name}/imdb_lstm_samples.json`);
    }

    let output_table = document.getElementById('result');
    resetOutputTable(output_table);

    let total_elapsed_time = 0;
    for (let i = 0; i < test_samples.length; i++) {
        let sample = test_samples[i];
        run_if.inputViews[0].set(sample.x);
        console.log(`ground truth: ${sample.y}`);
        console.log(`original model output: ${sample.orig_pred}`);

        let start = performance.now();
        await run_if.run();
        total_elapsed_time += performance.now() - start;

        let out_vec = run_if.outputViews[0].toActual();
        let pred_value = out_vec[0];
        console.log(`predicted: ${pred_value}`);
        console.log(out_vec);
        displayPrediction(output_table, sample.x, pred_value, sample.y);
    }
    console.log(`Total Elapsed Time[ms/image]: ${(total_elapsed_time / test_samples.length).toFixed(2)}`);
}

async function fetchSamples(path) {
    let response = await fetch(path);
    if (!response.ok) {
        throw new Error('Failed to load test samples');
    }
    let json = await response.json();
    let samples = [];
    for (let i = 0; i < json.length; i++) {
        samples.push({ 'x': new Float32Array(json[i]['x']), 'y': json[i]['y'], 'orig_pred': json[i]['orig_pred'] });
    }

    return samples;
}

function resetOutputTable(table) {
    let rows = table.children;
    for (let i = rows.length - 1; i >= 1; i--) {
        table.removeChild(rows[i]);
    }
}

function displayPrediction(table, input_image, prediction, ground_truth) {
    let tr = document.createElement('tr');
    tr.appendChild(document.createElement('td')).textContent = '' + input_image;
    tr.appendChild(document.createElement('td')).textContent = '' + prediction;
    tr.appendChild(document.createElement('td')).textContent = '' + ground_truth;

    table.appendChild(tr);
}
