'use strict';

let $ = (q, e) => (e || document).querySelector(q);
let flagInitialized = false;
let runner = null;

document.addEventListener('DOMContentLoaded', initialize);

async function main() {
    try {
        await run();
    } catch (e) {
        console.error(e);
    }
}

function loadImage(src) {
    return new Promise((resolve, reject) => {
        let img = new Image();

        img.addEventListener('load', () => {
            let ctx = $('#src').getContext('2d');
            ctx.drawImage(img, 0, 0);

            console.log('image loaded');
            resolve();
        });
        img.addEventListener('error', reject);

        img.src = src;
    })
}


async function initialize() {
    await WebDNN.init();

    console.log('compile pipeline');
    let pipelineData = await((await fetch(`./output/graph_webgpu.json?t=${Date.now()}`)).json());
    runner = WebDNN.gpu.createDNNDescriptorRunner(pipelineData);
    await runner.compile();
    console.log('compile pipeline: Done');

    console.log('load weight');
    await runner.loadWeights(new Uint8Array(await ((await fetch(`./output/weight_webgpu.bin?t=${Date.now()}`)).arrayBuffer())));
    console.log('load weight: Done');

    await loadImage("./image.jpg");
    flagInitialized = true;
}

async function run() {
    if (!flagInitialized) await initialize();

    let inputView = (await runner.getInputViews())[0];
    inputView.set(getImageData($('#src')));

    let outputView = (await runner.getOutputViews())[0];

    console.log('main processing');
    let start = performance.now();
    await runner.run();
    let totalElapsedTime = performance.now() - start;
    console.log('main processing: Done');

    setImageData($('#result'), outputView);
    console.log(`Total Elapsed Time[ms/image]: ${totalElapsedTime.toFixed(2)}`);
}

function setImageData(canvas, data) {
    let ctx = canvas.getContext('2d');
    let h = canvas.height;
    let w = canvas.width;
    let imageData = new ImageData(w, h);
    let pixelData = imageData.data;

    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            pixelData[(y * w + x) * 4] = data[(y * w + x) * 3];
            pixelData[(y * w + x) * 4 + 1] = data[(y * w + x) * 3 + 1];
            pixelData[(y * w + x) * 4 + 2] = data[(y * w + x) * 3 + 2];
            pixelData[(y * w + x) * 4 + 3] = 255;
        }
    }

    ctx.putImageData(imageData, 0, 0);
}

function getImageData(canvas) {
    let ctx = canvas.getContext('2d');
    let h = canvas.height;
    let w = canvas.width;
    let imageData = ctx.getImageData(0, 0, w, h);
    let pixelData = imageData.data;
    let data = new Float32Array(3 * h * w); //h,w,c(bgr)

    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            data[(y * w + x) * 3] = pixelData[(y * w + x) * 4];
            data[(y * w + x) * 3 + 1] = pixelData[(y * w + x) * 4 + 1];
            data[(y * w + x) * 3 + 2] = pixelData[(y * w + x) * 4 + 2];
        }
    }

    return data;
}
