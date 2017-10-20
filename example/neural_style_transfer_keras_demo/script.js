'use strict';

let runner = null;
let flagPaused = true;
let $input, $output;
let inputView, outputView;

const H = 144;
const W = 192;

document.addEventListener('DOMContentLoaded', initialize);

function togglePause() {
    flagPaused = !flagPaused;

    if (flagPaused) {
        setStatus('Paused');

    } else {
        setStatus('Running');
        mainRoutine();
    }
}

async function initialize() {
    try {
        runner = await WebDNN.load("./output");
        console.log(`backend: ${runner.backendName}`);

        $input = document.getElementById('input');
        $output = document.getElementById('output');
        inputView = runner.getInputViews()[0].toActual();
        outputView = runner.getOutputViews()[0].toActual();

        $input.srcObject = await (new WebCam()).getNextDeviceStream();

    } catch (err) {
        console.log(err);
        setStatus(`Error: ${err.message}`);
    }
}

async function mainRoutine() {
    if (flagPaused) return;

    inputView.set(await WebDNN.Image.getImageArray($input, {
        dstH: H, dstW: W,
        scale: [1, 1, 1],
        bias: [0, 0, 0],
        order: WebDNN.Image.Order.HWC,
        color: WebDNN.Image.Color.RGB
    }));

    await runner.run();

    WebDNN.Image.setImageArrayToCanvas(outputView, W, H, $output,{
        dstH: H, dstW: W,
        scale: [127.5, 127.5, 127.5],
        bias: [127.5, 127.5, 127.5],
        order: WebDNN.Image.Order.HWC,
        color: WebDNN.Image.Color.RGB
    });
    requestAnimationFrame(mainRoutine);
}

function setStatus(status) {
    document.getElementById('button').textContent = status;
}
