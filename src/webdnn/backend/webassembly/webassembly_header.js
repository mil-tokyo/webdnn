var Module = {};

// ES6 (let) cannot be used
onmessage = function (event) {
    switch (event.data.type) {
        case 'run':
            try {
                var data_offset = Module._get_data_buffer();
                for (var i = 0; i < event.data.inputs.length; i++) {
                    var var_alloc = event.data.inputs[i];
                    var data_buf = new Float32Array(Module.buffer, data_offset + var_alloc.offset * Float32Array.BYTES_PER_ELEMENT, var_alloc.size);
                    data_buf.set(var_alloc.data);
                }
                Module._run();
                var outputs = [];
                for (var i = 0; i < event.data.outputs.length; i++) {
                    var var_alloc = event.data.outputs[i];
                    var data_buf = new Float32Array(Module.buffer, data_offset + var_alloc.offset * Float32Array.BYTES_PER_ELEMENT, var_alloc.size);
                    outputs.push(data_buf);
                }
                postMessage(outputs);
            } catch (ex) {
                postMessage({ 'error': ex });
            }
            break;
        case 'weight':
            try {
                var weight_offset = Module._get_weight_buffer();
                var weight_buf = new Float32Array(Module.buffer, weight_offset, event.data.data.length);
                weight_buf.set(event.data.data);
                postMessage(0);
            } catch (ex) {
                postMessage({ 'error': ex });
            }
            break;
        default:
            postMessage({ 'error': new Error('Unknown message') });
            break;
    }
};

Module.quit = function (status, toThrow) {
    postMessage({ 'error': toThrow, 'status': status });
};

Module.onRuntimeInitialized = function () {
    postMessage(0);
}
