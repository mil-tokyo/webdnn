'use strict';

// Polyfill of Promise, fetch is needed

var run_if;

function run() {
    if (!run_if) {
        var backend_name = $('input[name=backend_name]:checked').val();
        WebDNN.prepareAll('./output', backend_name).then(function (result) {
            run_if = result;
            console.info('Backend: ' + run_if.backendName);
            run();
            return;
        }).catch(function (reason) {
            console.error('Initialization failed: ' + reason);
        });
        return;
    }

    fetchSamples('../../resources/mnist/test_samples.json').then(function (result) {
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
                var pred_label = 0;
                var pred_score = -Infinity;
                for (var j = 0; j < out_vec.length; j++) {
                    if (out_vec[j] > pred_score) {
                        pred_score = out_vec[j];
                        pred_label = j;
                    }
                }
                console.log('predicted: ' + pred_label);
                console.log(out_vec);

                i++;
                loop_code();
            });
        };

        loop_code();
    }).catch(function (reason) {
        console.error('Loading test samples failed: ' + reason);
    });

}

function makeMatFromJson(mat_data) {
    var mat = new Float32Array(mat_data['data']);
    return mat;
}

function fetchSamples(path) {
    return fetch(path).then(function (response) {
        return response.json();
    }).then(function (json) {
        var samples = [];
        for (var i = 0; i < json.length; i++) {
            samples.push({ 'x': makeMatFromJson(json[i]['x']), 'y': json[i]['y'] });
        }
        return samples;
    }).catch(function (reason) {
        return Promise.reject(reason);
    });
}
