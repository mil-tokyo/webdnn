'use strict';

let runner;
let x, y;

async function init() {
    // (1.1) Initialize DescriptorRunner
    runner = await WebDNN.load('./output');

    // (1.2) Get input and output variables
    x = runner.inputs[0];
    y = runner.outputs[0];

    document.querySelector('button').disabled = false;
}

async function run() {
    if (!runner) await init();

    // (2.1) Set input data
    x.set(await WebDNN.Image.getImageArray(document.querySelector('img'), {
        dstW: 227, dstH: 227,
        bias: [123.68, 116.779, 103.939],
        color: WebDNN.Image.Color.RGB,
        order: WebDNN.Image.Order.CHW
    }));

    // (2.2) Run DNN model
    await runner.run();

    // (2.3) Show computed vector and predicted label.
    let y_vec = y.toActual();
    let y_ids = WebDNN.Math.argmax(y_vec, 5); // Top 5
    console.log('Computed vector', y_vec);
    console.log('Predicted Label', y_ids.map(id => imagenet_labels[id])); // imagenet_labels is defined in "/data/imagenet_labels.js"
}

window.onload = () => init();
