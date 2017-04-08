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
  if (!$M) {
    await init();
  }

  let pipeline_data = JSON.parse($('#dnn_pipeline').val());
  runner = new $M.DNNPipelineRunner(pipeline_data, $Mg.webgpuHandler);
  runner.compile();

  let weights_data = await fetchWeights('mnist/mnist_weights.bin');
  let test_samples = await fetchSamples('mnist/test_samples.json');
  await runner.loadWeights(weights_data);

  for (let i = 0; i < test_samples.length; i++) {
    let sample = test_samples[i];
    console.log(`ground truth: ${sample.y}`);
    let output_mats = await runner.run([sample.x], [0], [5]);

    let out_vec = output_mats[0].data;
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

async function init() {
  $M = WebDNN;
  let backend = await $M.init();
  console.log(`backend: ${backend}`);
  $Mg = $M.gpu;
}

function makeMatFromJson(mat_data) {
  var mat = new $M.MatrixCPU(mat_data['shape'], new Float32Array(mat_data['data']));
  return mat;
}

async function fetchWeights(path) {
  let response = await fetch(path);
  let ab = await response.arrayBuffer();
  let weights_data = new Float32Array(ab);

  return weights_data;
}

async function fetchSamples(path) {
  let response = await fetch(path);
  let json = await response.json();
  let samples = [];
  for (let i = 0; i < json.length; i++) {
    samples.push({'x': makeMatFromJson(json[i]['x']), 'y': json[i]['y']});
  }

  return samples;
}
