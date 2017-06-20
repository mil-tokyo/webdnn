/// <reference path="../buffer/buffer_webgpu.ts" />
/// <reference path="../webgpu_handler.ts" />
/// <reference path="./descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />
/// <reference path="../fetch.ts" />
/// <reference path="../graph_descriptor/graph_descriptor_webgpu.ts" />
/// <reference path="../symbolic_array_buffer_view.ts" />
/// <reference path="../placeholder.ts" />

namespace WebDNN {
    export class DescriptorRunnerWebGPU extends DescriptorRunner<GraphDescriptorWebGPU> {
        readonly backendName = 'webgpu';

        webgpuHandler: WebGPUHandler;
        shaderLanguage: string;

        staticBuffer: BufferWebGPU | null;
        dynamicBuffer: BufferWebGPU | null;
        metaBuffers: BufferWebGPU[] | null;

        private inputViews: SymbolicFloat32Array[] | null;
        private outputViews: SymbolicFloat32Array[] | null;

        //noinspection JSUnusedLocalSymbols
        constructor(option?: any) {
            super();
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

            this.initializeBasicKernels();
        }

        private initializeBasicKernels() {
            this.webgpuHandler.loadKernel('kernel void sync(){}', 'basic');
        }

        async load(directory: string, progressCallback?: (loaded: number, total: number) => any) {

            let descriptorUrl = `${directory}/graph_${this.backendName}.json`;
            let weightUrl = `${directory}/weight_${this.backendName}.bin`;

            if (this.ignoreCache) {
                descriptorUrl += '?t=' + Date.now();
                weightUrl += '?t=' + Date.now();
            }

            descriptorUrl = transformUrl(descriptorUrl);
            weightUrl = transformUrl(weightUrl);

            let descriptorResponse = await WebDNN.fetch(descriptorUrl);
            let weightResponse = await WebDNN.fetch(weightUrl);

            let [descriptor, weightRawArray] = await Promise.all([
                await descriptorResponse.json(),
                await readArrayBufferProgressively(weightResponse, progressCallback)
            ]);

            await this.setDescriptor(descriptor);
            await this.compile();
            await this.initializeStaticBuffer(weightRawArray);
            await this.initializeMetaBuffers();
            if (this.placeholderContext && this.placeholderContext.isResolved) await this.initializeDynamicBuffer();
        }

        async initializeStaticBuffer(weightRawArray: ArrayBuffer) {
            if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
            let descriptor = this.descriptor;

            let staticBuffer = new BufferWebGPU(descriptor.memory_layout.static.size * Float32Array.BYTES_PER_ELEMENT);
            this.staticBuffer = staticBuffer;

            let decoder = get_weight_decoder(descriptor.weight_encoding);
            await staticBuffer.write(await decoder.decode(new Uint8Array(weightRawArray), descriptor.memory_layout));

            //assign buffer to input/output buffer view
            (await this.getInputViews()).forEach(view => {
                if (view.isDynamic) return;
                view.setArrayBuffer(staticBuffer.bufferView.buffer)
            });

            (await this.getOutputViews()).forEach(view => {
                if (view.isDynamic) return;
                view.setArrayBuffer(staticBuffer.bufferView.buffer)
            });
        }

        async initializeMetaBuffers() {
            if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");

            this.metaBuffers = await Promise.all<BufferWebGPU>(
                this.descriptor.exec_infos.map(async executionInfo => {
                    let buffer = new BufferWebGPU(executionInfo.meta_buffer.length * Int32Array.BYTES_PER_ELEMENT);
                    await buffer.write(new Uint8Array(executionInfo.meta_buffer));

                    return buffer;
                })
            );
        }

        async initializeDynamicBuffer() {
            if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
            if (!this.placeholderContext) throw Error("PlaceholderContext is not initialized.");
            if (!this.placeholderContext.isResolved) throw new Error(`Not all placeholders are resolved: ${this.placeholderContext}`);

            let dynamicBufferSize = this.placeholderContext.resolve(this.descriptor.memory_layout.dynamic.size);
            let dynamicBuffer = new BufferWebGPU(dynamicBufferSize * Float32Array.BYTES_PER_ELEMENT);
            this.dynamicBuffer = dynamicBuffer;

            (await this.getInputViews()).forEach(view => {
                if (!view.isDynamic) return;
                view.setArrayBuffer(dynamicBuffer.bufferView.buffer)
            });

            (await this.getOutputViews()).forEach(view => {
                if (!view.isDynamic) return;
                view.setArrayBuffer(dynamicBuffer.bufferView.buffer)
            });
        }

        async setDescriptor(descriptor: GraphDescriptorWebGPU) {
            this.descriptor = descriptor;

            //reset all datum depend on old descriptor
            this.staticBuffer = null;
            this.dynamicBuffer = null;
            this.metaBuffers = null;
            this.placeholderContext = new PlaceholderContext(descriptor.placeholders);
        }

        async compile() {
            if (!this.descriptor) throw new Error('Descriptor is not loaded');

            this.webgpuHandler.loadKernel(this.descriptor.kernel_source, 'descriptor');
        }

        async setPlaceholderValue(values: { [key: string]: number }) {
            if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized.');
            let placeholderContext = this.placeholderContext;

            placeholderContext.update(values);
            if (!placeholderContext.isResolved) return;

            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            if (!this.metaBuffers) throw new Error('MetaBuffers are not initialized');

            let descriptor = this.descriptor;
            let metaBuffers = this.metaBuffers;
            let executionInfos = descriptor.exec_infos;

            // resolve placeholders in dynamic buffer
            await this.initializeDynamicBuffer();
            if (!this.dynamicBuffer) throw new Error('DynamicBuffer is not initialized');
            let dynamicBuffer = this.dynamicBuffer;

            // resolve placeholders in execution info
            await Promise.all(
                executionInfos.map(async (executionInfo, i) => {

                    // resolve placeholders in meta buffer
                    let bufferView = new Int32Array(metaBuffers[i].bufferView.buffer);
                    for (let unresolved_value of executionInfo.unresolved_value_list) {
                        bufferView[unresolved_value.offset] = placeholderContext.resolve(unresolved_value.placeholder);
                    }

                    let threadgroupsPerGrid = executionInfo.threadgroups_per_grid;
                    threadgroupsPerGrid.width = placeholderContext.resolve(threadgroupsPerGrid.width);
                    threadgroupsPerGrid.height = placeholderContext.resolve(threadgroupsPerGrid.height);
                    threadgroupsPerGrid.depth = placeholderContext.resolve(threadgroupsPerGrid.depth);

                    let threadsPerThreadGroup = executionInfo.threads_per_thread_group;
                    threadsPerThreadGroup.width = placeholderContext.resolve(threadsPerThreadGroup.width);
                    threadsPerThreadGroup.height = placeholderContext.resolve(threadsPerThreadGroup.height);
                    threadsPerThreadGroup.depth = placeholderContext.resolve(threadsPerThreadGroup.depth);
                })
            );
        }

        async getInputViews() {
            if (this.inputViews) return this.inputViews;

            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');

            let descriptor = this.descriptor;
            let placeholderContext = this.placeholderContext;

            this.inputViews = descriptor.inputs.map(name => {
                let allocation = descriptor.memory_layout.static.allocations[name] || descriptor.memory_layout.dynamic.allocations[name];
                let view = new SymbolicFloat32Array(allocation, placeholderContext);

                return view;
            });

            return this.inputViews;
        }

        async getOutputViews() {
            if (this.outputViews) return this.outputViews;

            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');

            let descriptor = this.descriptor;
            let placeholderContext = this.placeholderContext;

            this.outputViews = descriptor.outputs.map(name => {
                let allocation = descriptor.memory_layout.static.allocations[name] || descriptor.memory_layout.dynamic.allocations[name];
                let view = new SymbolicFloat32Array(allocation, placeholderContext);

                return view;
            });

            return this.outputViews;
        }

        async run(): Promise<void> {
            if (!this.descriptor) throw new Error('GraphDescriptor is not loaded');
            if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');
            if (!this.staticBuffer) throw new Error('StaticBuffer is not initialized');
            if (!this.dynamicBuffer) throw new Error('DynamicBuffer is not initialized');
            if (!this.metaBuffers) throw new Error('MetaBuffer is not initialized');
            if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');
            if (!this.placeholderContext.isResolved) throw new Error(`Not all placeholders are resolved: ${this.placeholderContext}`);

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
