'use strict';

let $ = (q, e) => (e || document).querySelector(q);
let runner = null;
let flagPaused = true;

document.addEventListener('DOMContentLoaded', initialize);

function togglePause() {
    flagPaused = !flagPaused;
    if (flagPaused) {
        setStatus('Paused');
        $('#toggle').textContent = 'Restart';
    } else {
        setStatus('Running');
        $('#toggle').textContent = 'Pause';
        mainRoutine();
    }
}

async function initialize() {
    try {
        //noinspection ES6ModulesDependencies
        let backend = await WebDNN.init();
        console.log(`backend: ${backend}`);

        //noinspection JSUnresolvedFunction
        let pipelineData = await((await fetch(`./output/graph_${backend}.json?t=${Date.now()}`)).json());
        runner = WebDNN.gpu.createDNNDescriptorRunner(pipelineData);
        await runner.compile();

        //noinspection JSUnresolvedFunction
        await runner.loadWeights(new Uint8Array(await ((await fetch(`./output/weight_${backend}.bin?t=${Date.now()}`)).arrayBuffer())));

        Webcam.set({
            width: 512,
            height: 384,
            force_flash: true,
            image_format: 'jpeg',
            jpeg_quality: 10
        });
        Webcam.on('error', (err) => {
            throw err;
        });
        Webcam.on('live', () => {
            setStatus('Ready');
            let toggle = $('#toggle');
            toggle.textContent = 'Start';
            toggle.disabled = false;
        });
        Webcam.attach('#camera');
//noinspection ES6ModulesDependencies
    } catch (err) {
        console.log(err);
        setStatus(`Error: ${err.message}`);
    }
}

async function snap() {
    return new Promise(resolve => Webcam.snap(resolve, $('#snap')));
}

async function mainRoutine() {
    if (flagPaused) return;

    let inputView = (await runner.getInputViews())[0];
    let outputView = (await runner.getOutputViews())[0];

    await snap();
    inputView.set(getImageData($('#snap')));

    await runner.run();
    setImageData($('#result'), outputView);

    requestAnimationFrame(mainRoutine);
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
    let data = new Float32Array(3 * h * w);

    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            data[(y * w + x) * 3] = pixelData[(y * w + x) * 4];
            data[(y * w + x) * 3 + 1] = pixelData[(y * w + x) * 4 + 1];
            data[(y * w + x) * 3 + 2] = pixelData[(y * w + x) * 4 + 2];
        }
    }

    return data;
}

function setStatus(status) {
    $('#status').textContent = status;
}
