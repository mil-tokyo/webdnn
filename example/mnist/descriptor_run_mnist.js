'use strict';

var run_if;

function run_entry() {
    run().then(() => {
        console.log('run finished');
    }).catch((error) => {
        console.error('run failed ' + error);
    });
}

async function run() {
    if (!run_if) {
        let backend_name = $('input[name=backend_name]:checked').val();
        run_if = await WebDNN.prepareAll('./output', backend_name);
        console.info(`Backend: ${run_if.backendName}`);
    }

    let test_samples = await fetchSamples('../../resources/mnist/test_samples.json');

    let total_elapsed_time = 0;
    for (let i = 0; i < test_samples.length; i++) {
        let sample = test_samples[i];
        run_if.inputViews[0].set(sample.x);
        console.log(`ground truth: ${sample.y}`);

        let start = performance.now();
        await run_if.run();
        total_elapsed_time += performance.now() - start;

        let out_vec = run_if.outputViews[0];
        let pred_label = WebDNN.Math.argmax(out_vec)[0];
        // equivalent to
/*        let pred_label = 0;
        let pred_score = -Infinity;
        for (let j = 0; j < out_vec.length; j++) {
            if (out_vec[j] > pred_score) {
                pred_score = out_vec[j];
                pred_label = j;
            }
        }*/
        console.log(`predicted: ${pred_label}`);
        console.log(out_vec);
    }
    console.log(`Total Elapsed Time[ms/image]: ${(total_elapsed_time / test_samples.length).toFixed(2)}`);
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
