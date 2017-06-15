/// <reference path="../buffer/buffer_webgpu.ts" />
/// <reference path="../webgpu_handler.ts" />
/// <reference path="./descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />
/// <reference path="../fetch.ts" />
/// <reference path="../graph_descriptor/graph_descriptor_webgpu.ts" />
/// <reference path="../buffer_view.ts" />

namespace WebDNN {
    export class DescriptorRunnerWebGPU extends DescriptorRunner<GraphDescriptorWebGPU> {
        readonly backendName = 'webgpu';

        webgpuHandler: WebGPUHandler;
        shaderLanguage: string;
        staticBuffer: BufferWebGPU | null;
        dynamicBuffer: BufferWebGPU | null;
        metaBuffers: BufferWebGPU[] | null;
        inputViews: BufferView[] | null;
        outputViews: BufferView[] | null;

        constructor(option?: any) {
            super(option);
            if (!WebGPUHandler.isBrowserSupported) {
                throw new Error('WebGPU is not supported on this browser');
            }
        }

        async init() {
            // initialize webgpu, build kernels
            this.shaderLanguage = 'metal';
            this.webgpuHandler = new WebGPUHandler();
            await this.webgpuHandler.init();
            BufferWebGPU.init(this.webgpuHandler);

            this.init_basic_kernels();
        }

        private init_basic_kernels() {
            this.webgpuHandler.loadKernel('kernel void sync(){}', 'basic');
        }

        async load(directory: string, progressCallback?: (loaded: number, total: number) => any) {
            let graph_url = `${directory}/graph_${this.backendName}.json`;
            if (this.ignoreCache) {
                graph_url += '?t=' + Date.now();
            }
            graph_url = transformUrl(graph_url);
            let graph_fetch = await WebDNN.fetch(graph_url);
            if (!graph_fetch.ok) {
                throw new Error(`${graph_url} cannot be loaded`);
            }
            let descriptor = await graph_fetch.json();
            this.descriptor = descriptor;
            await this.compile();

            let weight_url = `${directory}/weight_${this.backendName}.bin`;
            if (this.ignoreCache) {
                weight_url += '?t=' + Date.now();
            }
            weight_url = transformUrl(weight_url);
            let weights_data_ab = await readArrayBufferProgressively(await WebDNN.fetch(weight_url, progressCallback), progressCallback);

            this.staticBuffer = new BufferWebGPU(descriptor.memory_layout.static.size * Float32Array.BYTES_PER_ELEMENT);
            let decoder = get_weight_decoder(descriptor.weight_encoding);
            await this.staticBuffer.write(await decoder.decode(new Uint8Array(weights_data_ab), descriptor.memory_layout));
        }

        setDescriptor(descriptor: GraphDescriptorWebGPU) {
            this.descriptor = descriptor;
        }

        async compile() {
            if (!this.descriptor) throw new Error('Descriptor is not loaded');

            this.webgpuHandler.loadKernel(this.descriptor.kernel_source, 'descriptor');
        }

        async setPlaceholder(values: { [key: string]: number }) {
            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            if (!this.staticBuffer) throw new Error('StaticBuffer is not initialized');

            let placeholders = Object.assign(this.descriptor.placeholders, values);

            for (let key in placeholders) {
                if (placeholders[key] == null) throw new Error(`Placeholder '${key}' is unresolved`);
            }

            //resolve placeholders
            let dynamicBufferSize = this.resolvePlaceHolder(this.descriptor.memory_layout.dynamic.size);
            this.dynamicBuffer = new BufferWebGPU(dynamicBufferSize * Float32Array.BYTES_PER_ELEMENT);

            this.metaBuffers = [];
            for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                let exec_info = this.descriptor.exec_infos[i];
                let metaBuffer8 = new Uint8Array(exec_info.meta_buffer);
                let metaBuffer32 = new Int32Array(metaBuffer8.buffer);

                //resolve unresolved metabuffer
                for (let unresolved_value of exec_info.unresolved_value_list) {
                    metaBuffer32[unresolved_value.offset] = this.resolvePlaceHolder(unresolved_value.placeholder);
                }

                let buf = new BufferWebGPU(exec_info.meta_buffer.length * Float32Array.BYTES_PER_ELEMENT);
                await buf.write(metaBuffer8);
                this.metaBuffers.push(buf);

                let threadgroups_per_grid = exec_info.threadgroups_per_grid;
                let threads_per_thread_group = exec_info.threads_per_thread_group;
                threadgroups_per_grid.width = this.resolvePlaceHolder(threadgroups_per_grid.width);
                threadgroups_per_grid.height = this.resolvePlaceHolder(threadgroups_per_grid.height);
                threadgroups_per_grid.depth = this.resolvePlaceHolder(threadgroups_per_grid.depth);
                threads_per_thread_group.width = this.resolvePlaceHolder(threads_per_thread_group.width);
                threads_per_thread_group.height = this.resolvePlaceHolder(threads_per_thread_group.height);
                threads_per_thread_group.depth = this.resolvePlaceHolder(threads_per_thread_group.depth);
            }

            let inputViews = await this.getInputViews();
            for (let i = 0; i < this.descriptor.inputs.length; i++) {
                if (this.descriptor.inputs[i] in this.descriptor.memory_layout.static.allocations) {
                    let allocation = this.descriptor.memory_layout.static.allocations[this.descriptor.inputs[i]];
                    inputViews[i].setFloat32Array(<Float32Array>this.staticBuffer.getWriteView(allocation.offset, allocation.size, Float32Array));

                } else {
                    let allocation = this.descriptor.memory_layout.dynamic.allocations[this.descriptor.inputs[i]];
                    let offset = this.resolvePlaceHolder(allocation.offset);
                    let size = this.resolvePlaceHolder(allocation.size);

                    inputViews[i].setFloat32Array(<Float32Array>this.dynamicBuffer.getWriteView(offset, size, Float32Array));
                }
            }

            let outputViews = await this.getOutputViews();
            for (let i = 0; i < this.descriptor.outputs.length; i++) {
                if (this.descriptor.outputs[i] in this.descriptor.memory_layout.static.allocations) {
                    let allocation = this.descriptor.memory_layout.static.allocations[this.descriptor.outputs[i]];
                    outputViews[i].setFloat32Array(<Float32Array>this.staticBuffer.getWriteView(allocation.offset, allocation.size, Float32Array));

                } else {
                    let allocation = this.descriptor.memory_layout.dynamic.allocations[this.descriptor.outputs[i]];
                    let offset = this.resolvePlaceHolder(allocation.offset);
                    let size = this.resolvePlaceHolder(allocation.size);

                    outputViews[i].setFloat32Array(<Float32Array>this.dynamicBuffer.getWriteView(offset, size, Float32Array));
                }
            }
        }

        async getInputViews() {
            if (this.inputViews) return this.inputViews;

            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            let views: BufferView[] = [];
            for (let i = 0; i < this.descriptor.inputs.length; i++) {
                views.push(new BufferView());
            }
            this.inputViews = views;
            return views;
        }

        resolvePlaceHolder(placeholder: number | PlaceHolder) {
            if (!this.descriptor) throw Error('Descriptor is not loaded');
            if (typeof placeholder == 'number') return placeholder;

            //noinspection JSUnusedLocalSymbols
            return ((placeholders) => eval(placeholder.eval))(this.descriptor.placeholders);
        }

        async getOutputViews() {
            if (this.outputViews) return this.outputViews;

            if (!this.descriptor) throw new Error('Descriptor is not loaded');

            let views: BufferView[] = [];
            for (let i = 0; i < this.descriptor.outputs.length; i++) {
                views.push(new BufferView());
            }
            this.outputViews = views;
            return views;
        }

        async run(): Promise<void> {
            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');
            if (!this.staticBuffer) throw new Error('Static buffer is not initialized');
            if (!this.dynamicBuffer) throw new Error('Dynamic buffer is not initialized');
            if (!this.metaBuffers) throw new Error('Meta buffer is not initialized');

            let staticBuffer = this.staticBuffer;
            let dynamicBuffer = this.dynamicBuffer;
            let metaBuffers = this.metaBuffers;

            if (WebDNN.DEBUG) {
                let records: any = [];
                let totalElapsedTime = 0;

                for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                    let exec_info = this.descriptor.exec_infos[i];

                    let start = performance.now();
                    await this.webgpuHandler.executeSinglePipelineState(
                        'descriptor.' + exec_info.entry_func_name,
                        exec_info.threadgroups_per_grid,
                        exec_info.threads_per_thread_group,
                        [staticBuffer, dynamicBuffer, metaBuffers[i]],
                        true
                    );
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

            } else {
                let complete_promise: Promise<void> | null = null;
                for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                    let exec_info = this.descriptor.exec_infos[i];
                    let is_last = i == this.descriptor.exec_infos.length - 1;
                    complete_promise = this.webgpuHandler.executeSinglePipelineState(
                        'descriptor.' + exec_info.entry_func_name,
                        exec_info.threadgroups_per_grid,
                        exec_info.threads_per_thread_group,
                        [staticBuffer, dynamicBuffer, metaBuffers[i]],
                        is_last
                    );
                }

                await complete_promise!;//wait to finish final kernel
            }
        }
    }
}
