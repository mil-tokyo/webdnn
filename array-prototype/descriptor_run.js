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
  runner = new $M.DNNDescriptorRunner(pipeline_data, $Mg.webgpuHandler);
  await runner.compile();

  runner.loadWeights(new Float32Array([2, 3, 5, 7, 1.1, -1.3]));

  let input_mat = new Float32Array([1.0, 0, -2.0]);
  let output_mats = await runner.run([input_mat]);
  console.log(output_mats[0]);
}

async function init() {
  $M = WebDNN;
  let backend = await $M.init();
  console.log(`backend: ${backend}`);
  $Mg = $M.gpu;
}
