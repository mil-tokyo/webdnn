var Module = {};

// ES6 (let) cannot be used
onmessage = function (event) {
    switch (event.data.type) {
        case 'run':
            try {
                var data_offset = [Module._get_static_buffer(), Module._get_dynamic_buffer()];
                for (var i = 0; i < event.data.inputs.length; i++) {
                    var var_alloc = event.data.inputs[i];
                    var data_buf = new Float32Array(Module.buffer, data_offset[var_alloc.space] + var_alloc.offset * Float32Array.BYTES_PER_ELEMENT, var_alloc.size);
                    data_buf.set(var_alloc.data);
                }

                Module._run();

                var outputs = [];
                var output_buffers = [];
                for (var i = 0; i < event.data.outputs.length; i++) {
                    var var_alloc = event.data.outputs[i];
                    var data_buf_view = new Float32Array(Module.buffer, data_offset[var_alloc.space] + var_alloc.offset * Float32Array.BYTES_PER_ELEMENT, var_alloc.size);
                    var data_buf_copy = new Float32Array(data_buf_view.length);
                    data_buf_copy.set(data_buf_view);
                    outputs.push(data_buf_copy);
                    output_buffers.push(data_buf_copy.buffer);
                }
                postMessage(outputs, output_buffers);
            } catch (ex) {
                postMessage({ 'error': ex.message });
            }
            break;

        case 'weight':
            try {
                var weight_buf = new Float32Array(Module.buffer, Module._get_static_buffer(), event.data.data.length);
                weight_buf.set(event.data.data);
                postMessage(0);
            } catch (ex) {
                postMessage({ 'error': ex.message });
            }
            break;

        case 'set_dynamic_buffer':
            try {
                // event.data = {size: number_of_elements, data = [kernel_order_0, offset0, value0, kernel_order_1, ...]}
                var dynamic_ptr = Module._allocate_dynamic_buffer(event.data.size);
                if (dynamic_ptr === 0) {
                    throw Error('Dynamic buffer cannot be allocated');
                }
                var data_to_set = event.data.data;
                var data_idx = 0;
                while (data_idx < data_to_set.length) {
                    Module._set_placeholder_value(data_to_set[data_idx], data_to_set[data_idx + 1], data_to_set[data_idx + 2]);
                    data_idx += 3;
                }
                postMessage(0);
            } catch (ex) {
                postMessage({ 'error': ex.message });
            }
            break;

        default:
            postMessage({ 'error': 'Unknown message' });
            break;
    }
};

Module.quit = function (status, toThrow) {
    postMessage({ 'error': toThrow, 'status': status });
};

Module.onRuntimeInitialized = function () {
    postMessage(0);
};
