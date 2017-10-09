'use strict';

async function run_entry() {
    try {
        await run();
        log('Run finished');

    } catch (error) {
        log('Error: ' + error);
    }
}

function log(msg) {
    let msg_node = document.getElementById('messages');
    msg_node.appendChild(document.createElement('br'));
    msg_node.appendChild(document.createTextNode(msg));
}

async function loadImage() {
    let imageData = await WebDNN.Image.getImageArray(document.getElementById("image_url").value, {dstW: 224, dstH: 224});
    WebDNN.Image.setImageArrayToCanvas(imageData, 224, 224, document.getElementById('input_image'));

    document.getElementById('run_button').disabled = false;
    log('Image loaded to canvas');
}

let runners = {};

function getFrameworkName() {
    return document.querySelector('input[name=framework]:checked').value;
}

async function prepare_run() {
    let backend_name = document.querySelector('input[name=backend]:checked').value;
    let framework_name = getFrameworkName();
    let backend_key = backend_name + framework_name;
    if (!(backend_key in runners)) {
        log('Initializing and loading model');
        let runner = await WebDNN.load(`./output_${framework_name}`, {backendOrder: backend_name});
        log(`Loaded backend: ${runner.backendName}, model converted from ${framework_name}`);

        runners[backend_key] = runner;
    } else {
        log('Model is already loaded');
    }
    return runners[backend_key];
}

async function run() {
    let runner = await prepare_run();

    runner.getInputViews()[0].set(await WebDNN.Image.getImageArray(document.getElementById('input_image'), {
        order: getFrameworkName() === 'chainer' ? WebDNN.Image.Order.CHW : WebDNN.Image.Order.HWC,
        color: WebDNN.Image.Color.BGR,
        bias: [123.68, 116.779, 103.939]
    }));

    let start = performance.now();
    await runner.run();
    let elapsed_time = performance.now() - start;

    let out_vec = runner.getOutputViews()[0].toActual();
    let top_labels = WebDNN.Math.argmax(out_vec, 5);

    let predicted_str = 'Predicted:';
    for (let j = 0; j < top_labels.length; j++) {
        predicted_str += ` ${top_labels[j]}(${imagenet_labels[top_labels[j]]})`;
    }
    log(predicted_str);

    console.log('output vector: ', out_vec);
    log(`Total Elapsed Time[ms/image]: ${elapsed_time.toFixed(2)}`);
}
