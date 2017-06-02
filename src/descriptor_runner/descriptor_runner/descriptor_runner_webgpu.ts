/// <reference path="../buffer/buffer_webgpu.ts" />
/// <reference path="../webgpu_handler.ts" />
/// <reference path="./descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />
/// <reference path="../fetch.ts" />
/// <reference path="../graph_descriptor/graph_descriptor_webgpu.ts" />

namespace WebDNN {
    export class DescriptorRunnerWebGPU implements DescriptorRunner {
        private descriptor: GraphDescriptorWebGPU;
        private dataMat: BufferWebGPU;
        private metaBufferGPUBuffers: BufferWebGPU[];
        public ignoreCache: boolean = false;
        public backend: string = 'webgpu';
        private inputViews: Float32Array[];
        private outputViews: Float32Array[];

        constructor(private webGPUHandler: WebGPUHandler) {

        }

        async load(directory: string, progressCallback?: (loaded: number, total: number) => any) {
            let graph_url = `${directory}/graph_${this.backend}.json`;
            if (this.ignoreCache) {
                graph_url += '?t=' + Date.now();
            }
            graph_url = transformUrl(graph_url);
            let graph_fetch = await WebDNN.fetch(graph_url);
            if (!graph_fetch.ok) {
                throw new Error(`${graph_url} cannot be loaded`);
            }
            this.descriptor = await graph_fetch.json();
            await this.compile();

            let weight_url = `${directory}/weight_${this.backend}.bin`;
            if (this.ignoreCache) {
                weight_url += '?t=' + Date.now();
            }
            weight_url = transformUrl(weight_url);
            let weights_data_ab = await readArrayBufferProgressively(await WebDNN.fetch(weight_url, progressCallback), progressCallback);
            await this.loadWeights(new Uint8Array(weights_data_ab));
        }

        setDescriptor(descriptor: GraphDescriptorWebGPU) {
            this.descriptor = descriptor;
        }

        async compile() {
            this.webGPUHandler.loadKernel(this.descriptor.kernel_source, 'descriptor');
            this.dataMat = new BufferWebGPU(this.descriptor.memory_layout.total_size * Float32Array.BYTES_PER_ELEMENT);
            this.metaBufferGPUBuffers = [];
            for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                let exec_info = this.descriptor.exec_infos[i];
                let buf = new BufferWebGPU(exec_info.meta_buffer.length * Float32Array.BYTES_PER_ELEMENT);
                await buf.write(new Uint8Array(exec_info.meta_buffer));
                this.metaBufferGPUBuffers.push(buf);
            }
        }

        async loadWeights(data: Uint8Array) {
            let decoder = get_weight_decoder(this.descriptor.weight_encoding);
            await this.dataMat.write(await decoder.decode(data, this.descriptor.memory_layout));
        }

        async getInputViews(): Promise<Float32Array[]> {
            if (this.inputViews) {
                return this.inputViews;
            }
            let views: Float32Array[] = [];
            for (let i = 0; i < this.descriptor.inputs.length; i++) {
                let var_alloc = this.descriptor.memory_layout.allocations[this.descriptor.inputs[i]];
                views.push(<Float32Array>this.dataMat.getWriteView(var_alloc.offset, var_alloc.size, Float32Array));
            }
            this.inputViews = views;
            return views;
        }

        async getOutputViews(): Promise<Float32Array[]> {
            if (this.outputViews) {
                return this.outputViews;
            }
            let views: Float32Array[] = [];
            for (let i = 0; i < this.descriptor.outputs.length; i++) {
                let var_alloc = this.descriptor.memory_layout.allocations[this.descriptor.outputs[i]];
                views.push(<Float32Array>this.dataMat.getReadView(var_alloc.offset, var_alloc.size, Float32Array));
            }
            this.outputViews = views;
            return views;
        }

        async run(): Promise<void> {
            if (!this.inputViews || !this.outputViews) {
                throw new Error('getInputViews and getOutputViews must be called prior to run');
            }

            if (window['PROFILE']) {
                let records: any = [];
                let totalElapsedTime = 0;

                for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                    let exec_info = this.descriptor.exec_infos[i];

                    let start = performance.now();
                    await this.webGPUHandler.executeSinglePipelineState(
                        'descriptor.' + exec_info.entry_func_name,
                        exec_info.threadgroups_per_grid,
                        exec_info.threads_per_thread_group,
                        [this.dataMat, this.metaBufferGPUBuffers[i]],
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
                    complete_promise = this.webGPUHandler.executeSinglePipelineState(
                        'descriptor.' + exec_info.entry_func_name,
                        exec_info.threadgroups_per_grid,
                        exec_info.threads_per_thread_group,
                        [this.dataMat, this.metaBufferGPUBuffers[i]],
                        is_last
                    );
                }

                await complete_promise!;//wait to finish final kernel
            }
        }
    }
}
