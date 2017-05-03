var Module;

onmessage = function (event) {
    switch (event.data.type) {
        case 'run':
            let data_offset = Module._get_data_buffer();
            for (let i = 0; i < event.data.inputs.length; i++) {
                let var_alloc = event.data.inputs[i];
                let data_buf = new Float32Array(Module.buffer, data_offset + var_alloc.offset * Float32Array.BYTES_PER_ELEMENT, var_alloc.size);
                data_buf.set(var_alloc.data);
            }
            Module._run();
            let outputs = [];
            for (let i = 0; i < event.data.outputs.length; i++) {
                let var_alloc = event.data.outputs[i];
                let data_buf = new Float32Array(Module.buffer, data_offset + var_alloc.offset * Float32Array.BYTES_PER_ELEMENT, var_alloc.size);
                outputs.push(data_buf);
            }
            postMessage(outputs);
            break;
        case 'weight':
            let weight_offset = Module._get_weight_buffer();
            let weight_buf = new Float32Array(Module.buffer, weight_offset, event.data.data.length);
            weight_buf.set(event.data.data);
            postMessage('weight');
            break;
        case 'init':
            postMessage('init');
            break;
    }
};
