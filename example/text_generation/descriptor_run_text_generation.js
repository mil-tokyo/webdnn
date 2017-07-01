'use strict';

var metadata = null;

function run_entry() {
    run().then(() => {
        log('Run finished');
    }).catch((error) => {
        log('Error: ' + error);
    });
}

function run_change_seed() {
    let n_sent = metadata.example_sentences.length;
    document.querySelector('input[name=seed_text]').value = metadata.example_sentences[Math.floor(Math.random() * (n_sent + 1))];
}

function log(msg) {
    let msg_node = document.getElementById('messages');
    msg_node.appendChild(document.createElement('br'));
    msg_node.appendChild(document.createTextNode(msg));
}

let runners = {};

async function prepare_run() {
    let backend_name = document.querySelector('input[name=backend_name]:checked').value;
    let backend_key = backend_name;
    if (!(backend_key in runners)) {
        log('Initializing and loading model');
        let runner = await WebDNN.load(`./output`, { backendOrder: backend_name });
        log(`Loaded backend: ${runner.backendName}`);

        runners[backend_key] = runner;
    } else {
        log('Model is already loaded');
    }
    return runners[backend_key];
}

function sentence_to_array(sentence) {
    let maxlen = metadata.maxlen;
    let n_chars = metadata.n_chars;
    let array = new Float32Array(1 * maxlen * n_chars);//NTC order
    for (let i = 0; i < maxlen; i++) {
        let char = sentence[sentence.length - maxlen + i];
        let char_idx = metadata.char_indices[char];
        if (char_idx === void 0) {
            char_idx = 0;
        }
        array[i * n_chars + char_idx] = 1.0;
    }

    return array;
}

function sample_next_char(scores, temperature) {
    let probs = new Float32Array(metadata.n_chars);
    let prob_sum = 0.0;
    for (let i = 0; i < metadata.n_chars; i++) {
        let prob = Math.exp(Math.log(scores[i]) / temperature);
        prob_sum += prob;
        probs[i] = prob;
    }

    let char_idx = metadata.n_chars - 1;
    let rand = Math.random() * prob_sum;
    for (let i = 0; i < metadata.n_chars; i++) {
        rand -= probs[i];
        if (rand < 0.0) {
            char_idx = i;
            break;
        }
    }

    return metadata.indices_char['' + char_idx];
}

async function run() {
    let runner = await prepare_run();

    let sentence_seed = document.querySelector('#seed_text').textContent;
    let sentence = sentence_seed;

    for (let i = 0; i < 100; i++) {
        // input current sentence to the model
        runner.getInputViews()[0].set(sentence_to_array(sentence));

        // predict next character's probability
        await runner.run();
        let out_vec = runner.getOutputViews()[0].toActual();
        // sample next character
        let next_char = sample_next_char(out_vec, 1.0);
        sentence += next_char;
        console.log('output vector: ', out_vec);
    }
    document.getElementById('result_seed').textContent = sentence_seed;
    document.getElementById('result_generated').textContent = sentence.slice(sentence_seed.length);
}

document.addEventListener('DOMContentLoaded', async function (event) {
    try {
        let response = await fetch('output/model_setting.json');
        if (!response.ok) {
            throw new Error('Metadata HTTP response is not OK');
        }
        let json = await response.json();
        metadata = json;
        document.querySelector('#seed_text').textContent = metadata['example_sentences'][0];
        document.getElementById('run_button').disabled = false;
        document.getElementById('change_seed').disabled = false;
    } catch (error) {
        log('Failed to load metadata: ' + error);
    }
});
