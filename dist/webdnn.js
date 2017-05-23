/// <reference path="../graph_descriptor/graph_descriptor.ts" />
///<reference path="../descriptor_runner/descriptor_runner.ts" />
var WebDNN;
(function (WebDNN) {
    /**
     * Abstract buffer interface. Read/write transactions are regarded as asynchronous operation.
     */
    class Buffer {
        constructor(byteLength, backed) {
            this.byteLength = byteLength;
            this.backed = backed;
        }
    }
    WebDNN.Buffer = Buffer;
})(WebDNN || (WebDNN = {}));
/// <reference path="./buffer.ts" />
var WebDNN;
(function (WebDNN) {
    class BufferWebGPU extends WebDNN.Buffer {
        constructor(byteLength) {
            super(byteLength, 'webgpu');
            if (byteLength == 0) {
                byteLength = 4; //0 length buffer causes error
            }
            this.buffer = BufferWebGPU.webgpuHandler.createBuffer(new Uint8Array(byteLength));
            this.bufferView = new Uint8Array(this.buffer.contents);
        }
        // async: there may be platforms synchronization is needed before writing
        async write(src, dst_offset) {
            await BufferWebGPU.webgpuHandler.sync();
            let viewSameType = new src.constructor(this.bufferView.buffer);
            viewSameType.set(src, dst_offset);
        }
        async read(dst, src_offset = 0, length) {
            if (!dst) {
                throw new Error('dst cannot be null');
            }
            await BufferWebGPU.webgpuHandler.sync();
            if (this.byteLength === 0) {
                // nothing to read
                return;
            }
            let dst_constructor = dst.constructor; //e.g. Float32Array
            let viewSameType = new dst_constructor(this.bufferView.buffer, this.bufferView.byteOffset + src_offset * dst_constructor.BYTES_PER_ELEMENT, length);
            if (length === undefined) {
                length = viewSameType.length - src_offset;
            }
            dst.set(viewSameType);
            return;
        }
        static init(webgpuHandler) {
            this.webgpuHandler = webgpuHandler;
        }
        getWriteView(offset, length, number_type) {
            let viewSameType = new number_type(this.bufferView.buffer, this.bufferView.byteOffset + offset * number_type.BYTES_PER_ELEMENT, length);
            return viewSameType;
        }
        getReadView(offset, length, number_type) {
            let viewSameType = new number_type(this.bufferView.buffer, this.bufferView.byteOffset + offset * number_type.BYTES_PER_ELEMENT, length);
            return viewSameType;
        }
        async syncWriteViews() {
            // no sync needed
        }
        async syncReadViews() {
            // if the user awaits promise from final kernel execution, this function call is not needed.
            await BufferWebGPU.webgpuHandler.sync();
        }
    }
    WebDNN.BufferWebGPU = BufferWebGPU;
})(WebDNN || (WebDNN = {}));
/// <reference path="./buffer/buffer_webgpu.ts" />
var WebDNN;
(function (WebDNN) {
    class WebGPUHandler {
        async init() {
            // asynchronous operation may be added in future
            if (!WebGPUHandler.isBrowserSupported) {
                throw new Error('This browser does not support WebGPU');
            }
            this.context = document.createElement('canvas').getContext('webgpu'); //force cast
            this.commandQueue = this.context.createCommandQueue();
            this.pipelineStates = new Map();
        }
        createBuffer(arrayBuffer) {
            return this.context.createBuffer(arrayBuffer);
        }
        loadKernel(librarySource, namespace = '') {
            let library = this.context.createLibrary(librarySource);
            for (let name of library.functionNames) {
                let kernelFunction = library.functionWithName(name);
                let pipelineStates = this.context.createComputePipelineState(kernelFunction);
                this.pipelineStates.set(namespace + '.' + name, pipelineStates);
            }
        }
        createCommandBuffer() {
            return this.commandQueue.createCommandBuffer();
        }
        getPipelineStateByName(name) {
            let state = this.pipelineStates.get(name);
            if (!state) {
                throw TypeError(`Kernel function "${name}" is not loaded.`);
            }
            return state;
        }
        executeSinglePipelineState(name, threadgroupsPerGrid, threadsPerThreadgroup, buffers, getCompletedPromise) {
            let commandBuffer = this.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();
            commandEncoder.setComputePipelineState(this.getPipelineStateByName(name));
            for (let i = 0; i < buffers.length; i++) {
                let buffer = buffers[i];
                let wgbuf;
                if (buffer instanceof WebDNN.BufferWebGPU) {
                    wgbuf = buffer.buffer;
                }
                else {
                    // cannot perform (buffer instanceof WebGPUBuffer) currently
                    wgbuf = buffer;
                }
                commandEncoder.setBuffer(wgbuf, 0, i);
            }
            commandEncoder.dispatch(threadgroupsPerGrid, threadsPerThreadgroup);
            commandEncoder.endEncoding();
            let promise = null;
            if (getCompletedPromise) {
                promise = commandBuffer.completed;
            }
            commandBuffer.commit();
            return promise;
        }
        async sync() {
            let commandBuffer = this.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();
            commandEncoder.setComputePipelineState(this.getPipelineStateByName('basic.sync'));
            commandEncoder.dispatch({
                width: 1,
                height: 1,
                depth: 1
            }, {
                width: 1,
                height: 1,
                depth: 1
            });
            commandEncoder.endEncoding();
            let promise = commandBuffer.completed;
            commandBuffer.commit();
            return promise;
        }
    }
    WebDNN.WebGPUHandler = WebGPUHandler;
    WebGPUHandler.isBrowserSupported = 'WebGPURenderingContext' in window && 'WebGPUComputeCommandEncoder' in window;
})(WebDNN || (WebDNN = {}));
///<reference path="./weight_decoder.ts" />
var WebDNN;
(function (WebDNN) {
    class WeightDecoderRaw {
        async decode(data, weight_allocation) {
            return new Float32Array(data.buffer, data.byteOffset, data.byteLength / 4);
        }
    }
    WebDNN.WeightDecoderRaw = WeightDecoderRaw;
})(WebDNN || (WebDNN = {}));
///<reference path="./weight_decoder_raw.ts" />
///<reference path="./weight_decoder.ts" />
var WebDNN;
(function (WebDNN) {
    class WeightDecoderEightbit {
        async decode(data, weight_allocation) {
            let dst = new Float32Array(weight_allocation.total_size);
            let data_view = new DataView(data.buffer, data.byteOffset);
            let src_offset = 0;
            while (src_offset < data.length) {
                let dst_offset = data_view.getInt32(src_offset, true);
                src_offset += 4;
                let body_size = data_view.getInt32(src_offset, true);
                src_offset += 4;
                let scale = data_view.getFloat32(src_offset, true);
                src_offset += 8;
                let scaled_table = new Float32Array(256);
                for (let i = 0; i < 256; i++) {
                    scaled_table[i] = WeightDecoderEightbit.decode_table[i & 0x7F] * scale * (i < 128 ? 1.0 : -1.0);
                }
                // do decode
                let src_data_view = new Uint8Array(data.buffer, data.byteOffset + src_offset, body_size);
                let inflate = new Zlib.Inflate(src_data_view);
                let decompressed = inflate.decompress();
                let dec_size = decompressed.length;
                for (let s = 0; s < dec_size; s++) {
                    dst[dst_offset++] = scaled_table[decompressed[s]];
                }
                src_offset += body_size;
            }
            return dst;
        }
    }
    WeightDecoderEightbit.decode_table = [0.0, 2.750000021e-06, 7.249999726e-06, 1.875000089e-05, 3.624999954e-05, 5.874999624e-05, 8.624999464e-05,
        1.437500032e-04, 2.312500001e-04, 3.187500115e-04, 4.062500084e-04, 5.187499919e-04, 6.562499912e-04,
        7.937499322e-04, 9.312499315e-04, 1.218750025e-03, 1.656249980e-03, 2.093750052e-03, 2.531250007e-03,
        2.968749963e-03, 3.406249918e-03, 3.843750106e-03, 4.281249829e-03, 4.843750037e-03, 5.531250034e-03,
        6.218749564e-03, 6.906249560e-03, 7.593749557e-03, 8.281249553e-03, 8.968749084e-03, 9.656248614e-03,
        1.109374966e-02, 1.328125037e-02, 1.546875015e-02, 1.765624993e-02, 1.984374970e-02, 2.203124948e-02,
        2.421874925e-02, 2.640625089e-02, 2.859375067e-02, 3.078125045e-02, 3.296874836e-02, 3.515625000e-02,
        3.734375164e-02, 3.953124955e-02, 4.171875119e-02, 4.390624911e-02, 4.671875015e-02, 5.015625060e-02,
        5.359374732e-02, 5.703124776e-02, 6.046874821e-02, 6.390624493e-02, 6.734374911e-02, 7.078124583e-02,
        7.421874255e-02, 7.765624672e-02, 8.109374344e-02, 8.453124017e-02, 8.796874434e-02, 9.140624106e-02,
        9.484373778e-02, 9.828124195e-02, 1.054687500e-01, 1.164062470e-01, 1.273437440e-01, 1.382812560e-01,
        1.492187530e-01, 1.601562500e-01, 1.710937470e-01, 1.820312440e-01, 1.929687560e-01, 2.039062530e-01,
        2.148437500e-01, 2.257812470e-01, 2.367187440e-01, 2.476562560e-01, 2.585937381e-01, 2.695312500e-01,
        2.804687619e-01, 2.914062440e-01, 3.023437560e-01, 3.132812381e-01, 3.242187500e-01, 3.351562619e-01,
        3.460937440e-01, 3.570312560e-01, 3.679687381e-01, 3.789062500e-01, 3.898437619e-01, 4.007812440e-01,
        4.117187560e-01, 4.226562381e-01, 4.335937500e-01, 4.445312619e-01, 4.585937560e-01, 4.757812321e-01,
        4.929687381e-01, 5.101562142e-01, 5.273437500e-01, 5.445312262e-01, 5.617187023e-01, 5.789062381e-01,
        5.960937142e-01, 6.132812500e-01, 6.304687262e-01, 6.476562023e-01, 6.648437381e-01, 6.820312142e-01,
        6.992186904e-01, 7.164062262e-01, 7.335937023e-01, 7.507811785e-01, 7.679687142e-01, 7.851561904e-01,
        8.023436666e-01, 8.195312023e-01, 8.367186785e-01, 8.539061546e-01, 8.710936904e-01, 8.882811666e-01,
        9.054686427e-01, 9.226561785e-01, 9.398436546e-01, 9.570311308e-01, 9.742186666e-01, 9.914061427e-01, 1.0,
    ];
    WebDNN.WeightDecoderEightbit = WeightDecoderEightbit;
})(WebDNN || (WebDNN = {}));
///<reference path="./weight_decoder.ts" />
///<reference path="./weight_decoder_raw.ts" />
///<reference path="./weight_decoder_eightbit.ts" />
var WebDNN;
(function (WebDNN) {
    function get_weight_decoder(name) {
        switch (name) {
            case 'raw':
                return new WebDNN.WeightDecoderRaw();
            case 'eightbit':
                return new WebDNN.WeightDecoderEightbit();
            default:
                throw new Error('Unknown weight encoding');
        }
    }
    WebDNN.get_weight_decoder = get_weight_decoder;
})(WebDNN || (WebDNN = {}));
var WebDNN;
(function (WebDNN) {
    var util;
    (function (util) {
        const NOT_SCHEDULED = -1;
        /**
         *  Schedule function which is called too much frequently.
         */
        class DispatchScheduler {
            constructor() {
                this.scheduledCallbackId = NOT_SCHEDULED;
            }
            /**
             * Register scheduled function. If already other function is scheduled, it is canceled and dispatcher will dispatch only
             * function which is registered at last.
             * @param fn scheduled function
             */
            request(fn) {
                this.fn = fn;
                if (this.scheduledCallbackId == NOT_SCHEDULED) {
                    this.scheduledCallbackId = requestAnimationFrame(() => this.forceDispatch());
                }
            }
            /**
             * Dispatch scheduled function just now. If no function is scheduled, dispatcher do nothing.
             */
            forceDispatch() {
                if (this.scheduledCallbackId == NOT_SCHEDULED)
                    return;
                this.cancel();
                this.fn();
            }
            /**
             * Cancel scheduled function. If no function is scheduled, dispatcher do nothing.
             */
            cancel() {
                if (this.scheduledCallbackId == NOT_SCHEDULED)
                    return;
                cancelAnimationFrame(this.scheduledCallbackId);
                this.scheduledCallbackId = NOT_SCHEDULED;
            }
        }
        util.DispatchScheduler = DispatchScheduler;
    })(util = WebDNN.util || (WebDNN.util = {}));
})(WebDNN || (WebDNN = {}));
/// <reference path="./util/dispatch_scheduler.ts" />
var WebDNN;
(function (WebDNN) {
    /**
     * Fetch delegate function.
     * Every fetch call in WebDNN is delegated to this function.
     * As default, `window.fetch` is set.
     * @type {(input:RequestInfo, init?:RequestInit)=>Promise<Response>}
     */
    let fetchDelegate = window.fetch;
    /**
     * Register delegate function for fetch
     * @param delegate delegate function
     */
    function registerFetchDelegate(delegate) {
        fetchDelegate = delegate;
    }
    WebDNN.registerFetchDelegate = registerFetchDelegate;
    /**
     * Fetch function. WebDNN API use this fetch function instead of original fetch function.
     * @param input Requested url
     * @param init Additional information about fetch
     * @returns Response
     */
    function fetch(input, init) {
        return fetchDelegate(input, init);
    }
    WebDNN.fetch = fetch;
    /**
     * Read `Response.body` stream as ArrayBuffer. This function provide progress information by callback.
     * @param res Response object
     * @param callback Callback function.
     * @returns ArrayBuffer
     */
    function readArrayBufferProgressively(res, callback) {
        if (!callback || !res.body)
            return res.arrayBuffer();
        let contentLength = res.headers.get('Content-Length');
        if (!contentLength)
            return res.arrayBuffer();
        const total = parseInt(contentLength);
        let buffer = new Uint8Array(total);
        let loaded = 0;
        let reader = res.body.getReader();
        let callbackScheduler = new WebDNN.util.DispatchScheduler();
        function accumulateLoadedSize(chunk) {
            buffer.set(chunk.value, loaded);
            loaded += chunk.value.length;
            if (callback) {
                callbackScheduler.request(() => callback(loaded, total));
            }
            if (loaded == total) {
                callbackScheduler.forceDispatch();
                return buffer.buffer;
            }
            else {
                return reader.read().then(accumulateLoadedSize);
            }
        }
        return reader.read().then(accumulateLoadedSize);
    }
    WebDNN.readArrayBufferProgressively = readArrayBufferProgressively;
})(WebDNN || (WebDNN = {}));
/// <reference path="./graph_descriptor.ts" />
/// <reference path="../buffer/buffer_webgpu.ts" />
/// <reference path="../webgpu_handler.ts" />
/// <reference path="./descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />
/// <reference path="../fetch.ts" />
/// <reference path="../graph_descriptor/graph_descriptor_webgpu.ts" />
var WebDNN;
(function (WebDNN) {
    class DescriptorRunnerWebGPU {
        constructor(webGPUHandler) {
            this.webGPUHandler = webGPUHandler;
            this.ignoreCache = false;
            this.backend = 'webgpu';
        }
        async load(directory, progressCallback) {
            let graph_url = `${directory}/graph_${this.backend}.json`;
            if (this.ignoreCache) {
                graph_url += '?t=' + Date.now();
            }
            this.descriptor = await (await WebDNN.fetch(graph_url, progressCallback)).json();
            await this.compile();
            let weight_url = `${directory}/weight_${this.backend}.bin`;
            if (this.ignoreCache) {
                weight_url += '?t=' + Date.now();
            }
            let weights_data_ab = await WebDNN.readArrayBufferProgressively(await WebDNN.fetch(weight_url, progressCallback), progressCallback);
            await this.loadWeights(new Uint8Array(weights_data_ab));
        }
        setDescriptor(descriptor) {
            this.descriptor = descriptor;
        }
        async compile() {
            this.webGPUHandler.loadKernel(this.descriptor.kernel_source, 'descriptor');
            this.weightMat = new WebDNN.BufferWebGPU(this.descriptor.weight_allocation.total_size * Float32Array.BYTES_PER_ELEMENT);
            this.dataMat = new WebDNN.BufferWebGPU(this.descriptor.variable_allocation.total_size * Float32Array.BYTES_PER_ELEMENT);
            this.metaBufferGPUBuffers = [];
            for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                let exec_info = this.descriptor.exec_infos[i];
                let buf = new WebDNN.BufferWebGPU(exec_info.meta_buffer.length * Float32Array.BYTES_PER_ELEMENT);
                await buf.write(new Uint8Array(exec_info.meta_buffer));
                this.metaBufferGPUBuffers.push(buf);
            }
        }
        async loadWeights(weightsData) {
            let decoder = WebDNN.get_weight_decoder(this.descriptor.weight_encoding);
            await this.weightMat.write(await decoder.decode(weightsData, this.descriptor.weight_allocation));
        }
        async getInputViews() {
            if (this.inputViews) {
                return this.inputViews;
            }
            let views = [];
            for (let i = 0; i < this.descriptor.inputs.length; i++) {
                let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.inputs[i]];
                views.push(this.dataMat.getWriteView(var_alloc.offset, var_alloc.size, Float32Array));
            }
            this.inputViews = views;
            return views;
        }
        async getOutputViews() {
            if (this.outputViews) {
                return this.outputViews;
            }
            let views = [];
            for (let i = 0; i < this.descriptor.outputs.length; i++) {
                let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.outputs[i]];
                views.push(this.dataMat.getReadView(var_alloc.offset, var_alloc.size, Float32Array));
            }
            this.outputViews = views;
            return views;
        }
        async run() {
            if (!this.inputViews || !this.outputViews) {
                throw new Error('getInputViews and getOutputViews must be called prior to run');
            }
            if (window['PROFILE']) {
                let records = [];
                let totalElapsedTime = 0;
                for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                    let exec_info = this.descriptor.exec_infos[i];
                    let start = performance.now();
                    await this.webGPUHandler.executeSinglePipelineState('descriptor.' + exec_info.entry_func_name, exec_info.threadgroups_per_grid, exec_info.threads_per_thread_group, [this.weightMat, this.dataMat, this.metaBufferGPUBuffers[i]], true);
                    let elapsedTime = performance.now() - start;
                    records.push({
                        'Kernel': exec_info.entry_func_name,
                        'Elapsed time [ms]': elapsedTime
                    });
                    totalElapsedTime += elapsedTime;
                }
                let summary = Array.from(Object.values(records.reduce((summary, record) => {
                    if (!(record['Kernel'] in summary)) {
                        summary[record['Kernel']] = {
                            'Kernel': record['Kernel'],
                            'Count': 0,
                            'Elapsed time [ms]': 0,
                        };
                    }
                    summary[record['Kernel']]['Count']++;
                    summary[record['Kernel']]['Elapsed time [ms]'] += record['Elapsed time [ms]'];
                    return summary;
                }, {})));
                summary.forEach(record => record['Ratio [%]'] = (record['Elapsed time [ms]'] / totalElapsedTime).toFixed(2));
                console.table(records);
                console.table(summary);
            }
            else {
                let complete_promise = null;
                for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                    let exec_info = this.descriptor.exec_infos[i];
                    let is_last = i == this.descriptor.exec_infos.length - 1;
                    complete_promise = this.webGPUHandler.executeSinglePipelineState('descriptor.' + exec_info.entry_func_name, exec_info.threadgroups_per_grid, exec_info.threads_per_thread_group, [this.weightMat, this.dataMat, this.metaBufferGPUBuffers[i]], is_last);
                }
                await complete_promise; //wait to finish final kernel
            }
        }
    }
    WebDNN.DescriptorRunnerWebGPU = DescriptorRunnerWebGPU;
})(WebDNN || (WebDNN = {}));
/// <reference path="../descriptor_runner/descriptor_runner_webgpu.ts" />
var WebDNN;
(function (WebDNN) {
    class GPUInterfaceWebGPU {
        constructor(option) {
            this.option = option;
            if (!WebDNN.WebGPUHandler.isBrowserSupported) {
                throw new Error('WebGPU is not supported on this browser');
            }
        }
        async init() {
            // initialize webgpu, build kernels
            this.shaderLanguage = 'metal';
            this.webgpuHandler = new WebDNN.WebGPUHandler();
            await this.webgpuHandler.init();
            WebDNN.BufferWebGPU.init(this.webgpuHandler);
            this.init_basic_kernels();
        }
        init_basic_kernels() {
            this.webgpuHandler.loadKernel('kernel void sync(){}', 'basic');
        }
        createDescriptorRunner() {
            return new WebDNN.DescriptorRunnerWebGPU(this.webgpuHandler);
        }
    }
    WebDNN.GPUInterfaceWebGPU = GPUInterfaceWebGPU;
})(WebDNN || (WebDNN = {}));
/// <reference path="./graph_descriptor.ts" />
/// <reference path="../webgpu_handler.ts" />
/// <reference path="./descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />
/// <reference path="../fetch.ts" />
/// <reference path="../graph_descriptor/graph_descriptor_webassembly.ts" />
var WebDNN;
(function (WebDNN) {
    class DescriptorRunnerWebassembly {
        constructor() {
            this.ignoreCache = false;
            this.backend = 'webassembly';
            this.worker_promise_reject_func = null;
            this.worker_initial_error = null;
        }
        async load(directory, progressCallback) {
            let graph_url = `${directory}/graph_${this.backend}.json`;
            if (this.ignoreCache) {
                graph_url += '?t=' + Date.now();
            }
            this.descriptor = await (await WebDNN.fetch(graph_url)).json();
            // for browsers which does not support wasm, try asm.js code
            let kernel_backend = typeof WebAssembly === 'object' ? 'webassembly' : 'asmjs';
            let worker_entry_js_path = `${directory}/kernels_${kernel_backend}.js`;
            if (this.ignoreCache) {
                worker_entry_js_path += '?t=' + Date.now();
            }
            this.worker_entry_js_path = worker_entry_js_path;
            await this.compile();
            let weight_url = `${directory}/weight_${this.backend}.bin`;
            if (this.ignoreCache) {
                weight_url += '?t=' + Date.now();
            }
            let weights_data_ab = await WebDNN.readArrayBufferProgressively(await WebDNN.fetch(weight_url), progressCallback);
            await this.loadWeights(new Uint8Array(weights_data_ab));
        }
        setDescriptor(descriptor) {
            this.descriptor = descriptor;
        }
        compile() {
            this.worker = new Worker(this.worker_entry_js_path);
            this.worker.onerror = (event) => {
                console.error('Worker Exception: ' + event.message);
                if (this.worker_promise_reject_func) {
                    this.worker_promise_reject_func(event);
                }
                else {
                    this.worker_initial_error = event;
                }
            };
            let promise = new Promise((resolve, reject) => {
                if (this.worker_initial_error) {
                    // occurs when this.worker_entry_js_path is 404
                    reject(this.worker_initial_error);
                    return;
                }
                this.worker_promise_reject_func = reject;
                this.worker.onmessage = (event) => {
                    if (event.data === 0) {
                        resolve();
                    }
                    else {
                        this.worker.terminate();
                        reject(new Error(event.data));
                    }
                };
                //this.worker.postMessage({ type: 'init' });
            });
            return promise;
        }
        async loadWeights(weightsData) {
            let decoder = WebDNN.get_weight_decoder(this.descriptor.weight_encoding);
            let weight_data = await decoder.decode(weightsData, this.descriptor.weight_allocation);
            let promise = new Promise((resolve, reject) => {
                this.worker_promise_reject_func = reject;
                this.worker.onmessage = (event) => {
                    if (event.data === 0) {
                        resolve();
                    }
                    else {
                        this.worker.terminate();
                        reject(new Error(event.data));
                    }
                };
                this.worker.postMessage({ type: 'weight', data: weight_data });
            });
            return promise;
        }
        async getInputViews() {
            if (this.inputViews) {
                return this.inputViews;
            }
            let views = [];
            for (let i = 0; i < this.descriptor.inputs.length; i++) {
                let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.inputs[i]];
                views.push(new Float32Array(var_alloc.size));
            }
            this.inputViews = views;
            return views;
        }
        async getOutputViews() {
            if (this.outputViews) {
                return this.outputViews;
            }
            let views = [];
            for (let i = 0; i < this.descriptor.outputs.length; i++) {
                let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.outputs[i]];
                views.push(new Float32Array(var_alloc.size));
            }
            this.outputViews = views;
            return views;
        }
        async run() {
            if (!this.inputViews || !this.outputViews) {
                throw new Error('getInputViews and getOutputViews must be called prior to run');
            }
            let promise = new Promise((resolve, reject) => {
                // TODO: better way not to generate function on every run
                this.worker_promise_reject_func = reject;
                this.worker.onmessage = (event) => {
                    if (Array.isArray(event.data)) {
                        for (let i = 0; i < event.data.length; i++) {
                            this.outputViews[i].set(event.data[i]);
                        }
                        resolve();
                    }
                    else {
                        this.worker.terminate();
                        reject(new Error(event.data));
                    }
                };
                let inputs = [];
                for (let i = 0; i < this.descriptor.inputs.length; i++) {
                    let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.inputs[i]];
                    inputs.push({ offset: var_alloc.offset, size: var_alloc.size, data: this.inputViews[i] });
                }
                let outputs = [];
                for (let i = 0; i < this.descriptor.outputs.length; i++) {
                    let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.outputs[i]];
                    outputs.push({ offset: var_alloc.offset, size: var_alloc.size });
                }
                this.worker.postMessage({ type: 'run', inputs: inputs, outputs: outputs });
            });
            return promise;
        }
    }
    WebDNN.DescriptorRunnerWebassembly = DescriptorRunnerWebassembly;
})(WebDNN || (WebDNN = {}));
/// <reference path="./gpu_interface.ts" />
/// <reference path="../descriptor_runner/descriptor_runner_webassembly.ts" />
var WebDNN;
(function (WebDNN) {
    class GPUInterfaceWebassembly {
        constructor(option) {
            this.option = option;
            if (typeof Worker === 'undefined') {
                throw new Error('WebWorker is needed for WebAssembly backend');
            }
            if (typeof WebAssembly !== 'object') {
                console.warn('WebAssembly is not supported on this browser, trying to use asm.js code');
            }
        }
        async init() {
        }
        createDescriptorRunner() {
            return new WebDNN.DescriptorRunnerWebassembly();
        }
    }
    WebDNN.GPUInterfaceWebassembly = GPUInterfaceWebassembly;
})(WebDNN || (WebDNN = {}));
/// <reference path="./graph_descriptor.ts" />
///<reference path="../fetch.ts" />
///<reference path="../graph_descriptor/graph_descriptor_fallback.ts" />
var WebDNN;
(function (WebDNN) {
    class DescriptorRunnerFallback {
        constructor() {
            this.ignoreCache = false;
            this.backend = 'fallback';
        }
        async load(directory, progressCallback) {
            let graph_url = `${directory}/graph_${this.backend}.json`;
            if (this.ignoreCache) {
                graph_url += '?t=' + Date.now();
            }
            this.descriptor = await (await WebDNN.fetch(graph_url)).json();
            await this.compile();
            let weight_url = `${directory}/weight_${this.backend}.bin`;
            if (this.ignoreCache) {
                weight_url += '?t=' + Date.now();
            }
            let weights_data_ab = await WebDNN.readArrayBufferProgressively(await WebDNN.fetch(weight_url), progressCallback);
            await this.loadWeights(new Uint8Array(weights_data_ab));
        }
        setDescriptor(descriptor) {
            this.descriptor = descriptor;
        }
        async compile() {
            this.compileKernel();
            this.rawWeightArray = new Float32Array(this.descriptor.weight_allocation.total_size);
            let weight_name_alloc = this.descriptor.weight_allocation.allocation;
            this.weightArrays = new Map();
            for (let name in weight_name_alloc) {
                let alloc = weight_name_alloc[name];
                this.weightArrays.set(name, new Float32Array(this.rawWeightArray.buffer, alloc.offset * Float32Array.BYTES_PER_ELEMENT, alloc.size));
            }
            this.variableArrays = new Map();
            let variable_name_alloc = this.descriptor.variable_allocation.allocation;
            for (let name in variable_name_alloc) {
                let alloc = variable_name_alloc[name];
                this.variableArrays.set(name, new Float32Array(alloc.size));
            }
        }
        compileKernel() {
            var dnn_fallback_kernel;
            eval(this.descriptor.kernel_source);
            this.kernelObj = dnn_fallback_kernel;
        }
        async loadWeights(weightsData) {
            // when weight format becomes not flat array (such as using quantization), the interface should be changed
            let decoder = WebDNN.get_weight_decoder(this.descriptor.weight_encoding);
            this.rawWeightArray.set(await decoder.decode(weightsData, this.descriptor.weight_allocation));
        }
        async run() {
            if (!this.inputViews || !this.outputViews) {
                throw new Error('getInputViews and getOutputViews must be called prior to run');
            }
            let run_entry_date = Date.now();
            let last_progress_date = Date.now(); //in milliseconds
            for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                let current_date = Date.now();
                if (current_date - last_progress_date >= 1000) {
                    let elapsed_ms = current_date - run_entry_date;
                    console.log(`Processed ${i}/${this.descriptor.exec_infos.length} kernels in ${elapsed_ms} ms`);
                    last_progress_date = current_date;
                    await this.wait_to_display();
                }
                let exec_info = this.descriptor.exec_infos[i];
                let input_arrays = exec_info.inputs.map((name) => this.variableArrays.get(name));
                let output_arrays = exec_info.outputs.map((name) => this.variableArrays.get(name));
                let weight_arrays = exec_info.weights.map((name) => this.weightArrays.get(name));
                this.kernelObj[exec_info.entry_func_name](input_arrays, output_arrays, weight_arrays, exec_info.call_option);
            }
            console.log(`Processed ${this.descriptor.exec_infos.length}/${this.descriptor.exec_infos.length} kernels in ${Date.now() - run_entry_date} ms`);
        }
        async wait_to_display() {
            // let console.log to be displayed, and prevent freeze
            return new Promise(function (resolve, reject) {
                setTimeout(resolve, 10);
            });
        }
        async getInputViews() {
            if (this.inputViews) {
                return this.inputViews;
            }
            let views = this.descriptor.inputs.map((name) => this.variableArrays.get(name));
            this.inputViews = views;
            return views;
        }
        async getOutputViews() {
            if (this.outputViews) {
                return this.outputViews;
            }
            let views = this.descriptor.outputs.map((name) => this.variableArrays.get(name));
            this.outputViews = views;
            return views;
        }
    }
    WebDNN.DescriptorRunnerFallback = DescriptorRunnerFallback;
})(WebDNN || (WebDNN = {}));
/// <reference path="../descriptor_runner/descriptor_runner_fallback.ts" />
var WebDNN;
(function (WebDNN) {
    class GPUInterfaceFallback {
        constructor(option) {
            this.option = option;
        }
        async init(option) {
        }
        createDescriptorRunner() {
            return new WebDNN.DescriptorRunnerFallback();
        }
    }
    WebDNN.GPUInterfaceFallback = GPUInterfaceFallback;
})(WebDNN || (WebDNN = {}));
///<reference path="./gpu_interface/gpu_interface.ts" />
///<reference path="./gpu_interface/gpu_interface_webgpu.ts" />
///<reference path="./gpu_interface/gpu_interface_webassembly.ts" />
///<reference path="./gpu_interface/gpu_interface_fallback.ts" />
var WebDNN;
(function (WebDNN) {
    let givenBackendOptions;
    let tryingBackendOrder;
    let loadedBackendName;
    async function tryInitNext() {
        let backend_name = tryingBackendOrder.shift();
        if (!backend_name) {
            throw new Error('No backend is available');
        }
        let option = givenBackendOptions[backend_name];
        let gpuif;
        try {
            switch (backend_name) {
                case 'webgpu':
                    gpuif = new WebDNN.GPUInterfaceWebGPU(option);
                    break;
                case 'webassembly':
                    gpuif = new WebDNN.GPUInterfaceWebassembly(option);
                    break;
                case 'fallback':
                    gpuif = new WebDNN.GPUInterfaceFallback(option);
                    break;
                default:
                    throw new Error('Unknown backend ' + backend_name);
            }
            await gpuif.init();
            WebDNN.gpu = gpuif;
            loadedBackendName = backend_name;
        }
        catch (ex) {
            console.warn(`Failed to initialize ${backend_name} backend: ${ex}`);
            return await tryInitNext();
        }
        return loadedBackendName;
    }
    async function init(backendOrder, backendOptions = {}) {
        if (!backendOrder) {
            backendOrder = ['webgpu', 'webassembly'];
        }
        else if (typeof backendOrder === 'string') {
            backendOrder = [backendOrder];
        }
        givenBackendOptions = backendOptions;
        tryingBackendOrder = backendOrder.concat(['fallback']);
        await tryInitNext();
        return loadedBackendName;
    }
    WebDNN.init = init;
    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param directory URL of directory that contains graph descriptor files (e.g. graph_fallback.json)
     * @param initOption Initialize option
     * @return Interface to input/output data and run the model.
     */
    async function prepareAll(directory, initOption = {}) {
        await init(initOption.backendOrder, initOption.backendOptions);
        while (true) {
            try {
                let runner = WebDNN.gpu.createDescriptorRunner();
                await runner.load(directory, initOption.progressCallback);
                let inputViews = await runner.getInputViews();
                let outputViews = await runner.getOutputViews();
                return {
                    backendName: loadedBackendName,
                    inputViews: inputViews,
                    outputViews: outputViews,
                    run: runner.run.bind(runner)
                };
            }
            catch (ex) {
                console.error(`Model loading failed for ${loadedBackendName} backend. Trying next backend. ${ex.message}`);
                await tryInitNext();
            }
        }
    }
    WebDNN.prepareAll = prepareAll;
})(WebDNN || (WebDNN = {}));
var WebDNN;
(function (WebDNN) {
    var Math;
    (function (Math) {
        /**
         * Return indices of the top-K largest samples.
         * @param arr array
         * @param k number of indices
         * @returns {number[]} indices of top-K largest samples
         */
        function argmax(arr, k = 1) {
            let stack = [[0, arr.length]];
            let workspace = {};
            while (stack.length > 0) {
                let fromTo = stack.shift(), from = fromTo[0], to = fromTo[1], pivot = arr[to - 1], left = from, right = to - 2, tmp;
                if (from >= to)
                    continue;
                while (true) {
                    while (arr[left] > pivot && left <= right)
                        left++;
                    while (arr[right] <= pivot && left <= right)
                        right--;
                    if (left >= right)
                        break;
                    tmp = arr[left] || left;
                    arr[left] = arr[right] || right;
                    arr[right] = tmp;
                    tmp = workspace[left] || left;
                    workspace[left] = workspace[right] || right;
                    workspace[right] = tmp;
                }
                if (left != to - 1) {
                    arr[to - 1] = arr[left];
                    arr[left] = pivot;
                    tmp = workspace[to - 1] || to - 1;
                    workspace[to - 1] = workspace[left] || left;
                    workspace[left] = tmp;
                }
                stack.unshift([from, left]);
                if (left + 1 < k)
                    stack.unshift([left + 1, to]);
            }
            let result = [];
            for (let i = 0; i < k; i++) {
                result.push(i in workspace ? workspace[i] : i);
            }
            return result;
        }
        Math.argmax = argmax;
        /**
         * Return indices of the top-K smallest samples.
         * @param arr array
         * @param k number of indices
         * @returns {number[]} indices of top-K smallest samples
         */
        function argmin(arr, k = 1) {
            let stack = [[0, arr.length]];
            let workspace = {};
            while (stack.length > 0) {
                let fromTo = stack.shift(), from = fromTo[0], to = fromTo[1], pivot = arr[to - 1], left = from, right = to - 2, tmp;
                if (from >= to)
                    continue;
                while (true) {
                    while (arr[left] < pivot && left <= right)
                        left++;
                    while (arr[right] >= pivot && left <= right)
                        right--;
                    if (left >= right)
                        break;
                    tmp = arr[left] || left;
                    arr[left] = arr[right] || right;
                    arr[right] = tmp;
                    tmp = workspace[left] || left;
                    workspace[left] = workspace[right] || right;
                    workspace[right] = tmp;
                }
                if (left != to - 1) {
                    arr[to - 1] = arr[left];
                    arr[left] = pivot;
                    tmp = workspace[to - 1] || to - 1;
                    workspace[to - 1] = workspace[left] || left;
                    workspace[left] = tmp;
                }
                stack.unshift([from, left]);
                if (left + 1 < k)
                    stack.unshift([left + 1, to]);
            }
            let result = [];
            for (let i = 0; i < k; i++) {
                result.push(i in workspace ? workspace[i] : i);
            }
            return result;
        }
        Math.argmin = argmin;
    })(Math = WebDNN.Math || (WebDNN.Math = {}));
})(WebDNN || (WebDNN = {}));
//# sourceMappingURL=webdnn.js.map