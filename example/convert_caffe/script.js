'use strict';

let runner;
let x, y;

async function init() {
    // (1.1) Initialize DescriptorRunner
    runner = await WebDNN.load('./output');

    // (1.2) Get input and output variables
    x = runner.inputs[0];
    y = runner.outputs[0];
}

async function run() {
    // (2.1) Set input data
    x.set(await WebDNN.Image.getImageArray(document.querySelector('canvas'), {
        dstW: 227, dstH: 227,
        bias: [123.68, 116.779, 103.939],
        color: WebDNN.Image.Color.RGB,
        order: WebDNN.Image.Order.HWC
    }));

    // (2.2) Run DNN model
    await runner.run();

    // (2.3) Show computed vector and predicted label.
    let y_vec = y.toActual();
    console.log('Computed vector', y_vec);
    console.log('Predicted Label', WebDNN.Math.argmax(y_vec));
}

const SIZE = 227;
window.onload = () => init();
