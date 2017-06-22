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
        test_samples = await fetchSamples(`./output_${framework_name}/test_samples.json`);
    }

    let output_table = document.getElementById('result');
    resetOutputTable(output_table);

    await WebDNN.runner.setPlaceholderValue({
        N: 1
    });

    let total_elapsed_time = 0;
    for (let i = 0; i < test_samples.length; i++) {
        let sample = test_samples[i];
        run_if.inputViews[0].set(sample.x);
        console.log(`ground truth: ${sample.y}`);

        let start = performance.now();
        await run_if.run();
        total_elapsed_time += performance.now() - start;

        let out_vec = run_if.outputViews[0].toActual();
        let pred_label = WebDNN.Math.argmax(out_vec)[0];
        console.log(`predicted: ${pred_label}`);
        console.log(out_vec);
        displayPrediction(output_table, sample.x, pred_label, sample.y);
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
        samples.push({ 'x': new Float32Array(json[i]['x']), 'y': json[i]['y'] });
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
    let canvas = document.createElement('canvas');
    canvas.width = 28;
    canvas.height = 28;
    let ctx = canvas.getContext('2d');
    let img = ctx.createImageData(28, 28);
    for (let i = 0; i < 28 * 28; i++) {
        let pixel = input_image[i] * 255;
        img.data[i * 4 + 0] = pixel;//r
        img.data[i * 4 + 1] = pixel;//g
        img.data[i * 4 + 2] = pixel;//b
        img.data[i * 4 + 3] = 255;//a
    }
    ctx.putImageData(img, 0, 0);
    tr.appendChild(document.createElement('td')).appendChild(canvas);
    tr.appendChild(document.createElement('td')).textContent = '' + prediction;
    tr.appendChild(document.createElement('td')).textContent = '' + ground_truth;

    table.appendChild(tr);
}
