'use strict';

let $ = (q, e) => (e || document).querySelector(q);
let dnn = null;
let flagPaused = true;
let $input, $output;
let inputView, outputView;
let ctxIn, ctxOut;
let h, w;

document.addEventListener('DOMContentLoaded', initialize);

function togglePause() {
    flagPaused = !flagPaused;

    if (flagPaused) {
        $('.OutputLayer').style.display = 'none';
        $('.UILayer').style.display = '';
        setStatus('Paused');

    } else {
        $('.OutputLayer').style.display = '';
        $('.UILayer').style.display = 'none';
        setStatus('Running');
        mainRoutine();
    }
}

async function initialize() {
    try {
        //noinspection ES6ModulesDependencies
        dnn = await WebDNN.load("./output");
        console.log(`backend: ${dnn.backendName}`);

        Webcam.set({
            dest_width: 192,
            dest_height: 144,
            flip_horiz: true,
            image_format: 'png'
        });
        Webcam.on('error', (err) => {
            throw err;
        });
        Webcam.on('live', () => {
            setStatus('Ready');
        });
        Webcam.attach('.CameraLayer');

        $input = $('#snap');
        $output = $('#result');
        inputView = dnn.getInputViews()[0].toActual();
        outputView = dnn.getOutputViews()[0].toActual();
        ctxIn = $input.getContext('2d');
        ctxOut = $output.getContext('2d');
        h = $output.height;
        w = $output.width;

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

    await snap();
    getImageData();

    await dnn.run();
    setImageData();

    requestAnimationFrame(mainRoutine);
}

function getImageData() {
    let pixelData = ctxIn.getImageData(0, 0, w, h).data;

    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            inputView[(0 * h + y) * w + x] = pixelData[(y * w + x) * 4];
            inputView[(1 * h + y) * w + x] = pixelData[(y * w + x) * 4 + 1];
            inputView[(2 * h + y) * w + x] = pixelData[(y * w + x) * 4 + 2];
        }
    }
}

function setImageData() {
    let imageData = new ImageData(w, h);

    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            imageData.data[(y * w + x) * 4] = outputView[(0 * h + y) * w + x];
            imageData.data[(y * w + x) * 4 + 1] = outputView[(1 * h + y) * w + x];
            imageData.data[(y * w + x) * 4 + 2] = outputView[(2 * h + y) * w + x];
            imageData.data[(y * w + x) * 4 + 3] = 255;
        }
    }

    ctxOut.putImageData(imageData, 0, 0);
}

function setStatus(status) {
    $('#status').textContent = status;
}
