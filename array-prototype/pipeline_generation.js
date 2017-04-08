'use strict';

var $M, $Mg;

function generate() {
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

  let graph = JSON.parse($('#dnn_graph').val());
  $('#dnn_pipeline').val(JSON.stringify(graph));

  let generator = new $M.DNNPipelineGenerator();
  let pipeline = generator.generate(graph);

  $('#dnn_pipeline').val(JSON.stringify(pipeline, null, "  "));
}

async function init() {
  $M = WebDNN;
  let backend = await $M.init();
  console.log(`backend: ${backend}`);
  $Mg = $M.gpu;
}