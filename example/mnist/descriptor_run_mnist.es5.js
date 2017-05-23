'use strict';

// Polyfill of Promise, fetch is needed
// manually written for ES5 environment

var run_if = null;

function msg(s) {
    document.getElementById('msg_place').textContent = s;
}

function reset_backend() {
    run_if = null;
    resetOutputTable(document.getElementById('result'));
    msg('Resetted backend');
}

function run() {
    if (!run_if) {
        let backend_name = document.querySelector('input[name=backend_name]:checked').value;
        WebDNN.prepareAll('./output', { backendOrder: backend_name }).then(function (result) {
            run_if = result;
            msg('Backend: ' + run_if.backendName);
            console.info('Backend: ' + run_if.backendName);
            run();
        }).catch(function (reason) {
            console.error('Initialization failed: ' + reason);
        });
        return;
    }

    var output_table = document.getElementById('result');
    resetOutputTable(output_table);
    fetchSamples('./output/test_samples.json').then(function (result) {
        var test_samples = result;
        var total_elapsed_time = 0;
        var i = 0;
        var sample;
        var start;
        var loop_code = function () {
            if (i >= test_samples.length) {
                console.log('Total Elapsed Time[ms/image]: ' + (total_elapsed_time / test_samples.length).toFixed(2));
                return;
            }
            sample = test_samples[i];
            run_if.inputViews[0].set(sample.x);
            console.log('ground truth: ' + sample.y);

            start = performance.now();
            run_if.run().then(function () {

                total_elapsed_time += performance.now() - start;

                var out_vec = run_if.outputViews[0];
                var pred_label = WebDNN.Math.argmax(out_vec)[0];
                console.log('predicted: ' + pred_label);
                console.log(out_vec);
                displayPrediction(output_table, sample.x, pred_label, sample.y);

                i++;
                loop_code();
            });
        };

        loop_code();
    }).catch(function (reason) {
        console.error('Loading test samples failed: ' + reason);
    });

}

function fetchSamples(path) {
    return fetch(path).then(function (response) {
        return response.json();
    }).then(function (json) {
        var samples = [];
        for (var i = 0; i < json.length; i++) {
            samples.push({ 'x': new Float32Array(json[i]['x']), 'y': json[i]['y'] });
        }
        return samples;
    }).catch(function (reason) {
        return Promise.reject(reason);
    });
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
