'use strict';

var $M, $Mg;
var weights, samples, dnn;

function main() {
  run().then(() => {
    console.log('run finished');
  }).catch((error) => {
    console.error('run failed ' + error);
  });
}

async function run() {
  $M = WebDNN;
  let backend = await $M.init();
  console.log(`backend: ${backend}`);
  $Mg = $M.gpu;

  weights = await fetchWeights('mnist/mnist_weights.json');
  samples = await fetchSamples('mnist/test_samples.json');
  dnn = new $M.DNN();
  constructNet(dnn);
  dnn.dnnPipeline.setWeights(weights);

  for (let i = 0; i < samples.length; i++) {
    console.log(`sample ${i}`);
    let inVars = new Map([['x', samples[i]['x']]]);
    let outVars = await dnn.dnnPipeline.run(inVars, dnn);
    console.log(`ground truth: ${samples[i]['y']}`);
    let out_vec = outVars.get('l3').data;
    let pred_label = 0;
    let pred_score = -Infinity;
    for (let j = 0; j < out_vec.length; j++) {
      if (out_vec[j] > pred_score) {
        pred_score = out_vec[j];
        pred_label = j;
      }
    }
    console.log(`predicted label: ${pred_label}`);
    console.log(out_vec);
  }
}

function makeMatFromJson(mat_data) {
  var mat = new $M.MatrixCPU(mat_data['shape'], new Float32Array(mat_data['data']));
  return mat;
}

async function fetchWeights(path) {
  let response = await fetch(path);
  let json = await response.json();
  let weights = new Map();
  for (let key in json) {
    weights.set(key, makeMatFromJson(json[key]));
  }

  return weights;
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

function pushArray(dst, src) {
  Array.prototype.push.apply(dst, src);
}

function constructNet(dnn) {
  let pipeline = dnn.dnnPipeline;
  let operations = pipeline.operations;
  operations.push(new $M.DNNMalloc('l1', [1, 100]));
  let l1 = new $M.FullyConnectedLayer(new $M.DNNLayerIONames(['x'], ['l1'], ['l1/W', 'l1/b']), {'inDim': 784, 'outDim': 100});
  pushArray(operations, l1.getKernel(1));
  let relu1 = new $M.ReluLayer(new $M.DNNLayerIONames(['l1'], ['l1']), {'size': 100});
  pushArray(operations, relu1.getKernel(1));

  operations.push(new $M.DNNMalloc('l2', [1, 100]));
  let l2 = new $M.FullyConnectedLayer(new $M.DNNLayerIONames(['l1'], ['l2'], ['l2/W', 'l2/b']), {'inDim': 100, 'outDim': 100});
  pushArray(operations, l2.getKernel(1));
  operations.push(new $M.DNNFree('l1'));
  let relu2 = new $M.ReluLayer(new $M.DNNLayerIONames(['l2'], ['l2']), {'size': 100});
  pushArray(operations, relu2.getKernel(1));

  operations.push(new $M.DNNMalloc('l3', [1, 10]));
  let l3 = new $M.FullyConnectedLayer(new $M.DNNLayerIONames(['l2'], ['l3'], ['l3/W', 'l3/b']), {'inDim': 100, 'outDim': 10});
  pushArray(operations, l3.getKernel(1));
  operations.push(new $M.DNNFree('l2'));

}
