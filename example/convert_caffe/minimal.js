'use strict';

let runner;
let x, y;

async function init() {
    // (1.1) Initialize DescriptorRunner
    runner = await WebDNN.load('./output');

    // (1.2) Get input and output variables
    x = runner.getInputViews()[0].toActual();
    y = runner.getOutputViews()[0].toActual();
}

async function run() {
    // (2.1) Set input data
    x.set(loadImageData());

    // (2.2) Run DNN model
    await runner.run();

    // (2.3) Show computed vector and predicted label.
    console.log('Computed vector', y);
    console.log('Predicted Label', WebDNN.Math.argmax(y));
}

const SIZE = 227;
window.onload = () => init();

function loadImage() {
    let img = new Image();

    img.onload = () => document.querySelector('canvas').getContext('2d').drawImage(img, 0, 0, SIZE, SIZE);
    img.src = document.querySelector('input').value;
}

function loadImageData() {
    let data = document.querySelector('canvas').getContext('2d').getImageData(0, 0, SIZE, SIZE).data;
    let mean = [123.68, 116.779, 103.939];

    let res = new Float32Array(3 * SIZE * SIZE);

    for (let y = 0; y < SIZE; y++) {
        for (let x = 0; x < SIZE; x++) {
            // NOTE: The channel order of input image of CaffeNet is BGR.
            // Therefore follows code change the channel order from RGB to BGR.
            res[(y * SIZE + x) * 3] = data[(y * SIZE + x) * 4 + 2] - mean[2];
            res[(y * SIZE + x) * 3 + 1] = data[(y * SIZE + x) * 4 + 1] - mean[1];
            res[(y * SIZE + x) * 3 + 2] = data[(y * SIZE + x) * 4] - mean[0];
        }
    }

    return res;
}
