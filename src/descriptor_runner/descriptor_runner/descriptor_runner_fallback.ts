///<reference path="../fetch.ts" />
///<reference path="../graph_descriptor/graph_descriptor_fallback.ts" />

namespace WebDNN {
    export class DescriptorRunnerFallback extends DescriptorRunner<GraphDescriptorFallback> {
        readonly backendName = 'fallback';

        private kernelObj: any;
        private rawArray: Float32Array | null;
        private variableArrays: Map<string, Float32Array> | null;
        private inputViews: Float32Array[] | null;
        private outputViews: Float32Array[] | null;

        init(): Promise<void> {
            //nothing to do
            return Promise.resolve();
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
            this.descriptor = await graph_fetch.json();
            await this.compile();

            let weight_url = `${directory}/weight_${this.backendName}.bin`;
            if (this.ignoreCache) {
                weight_url += '?t=' + Date.now();
            }
            weight_url = transformUrl(weight_url);
            let weights_data_ab = await readArrayBufferProgressively(await WebDNN.fetch(weight_url), progressCallback);
            await this.loadWeights(new Uint8Array(weights_data_ab));
        }

        setPlaceholderValue(placeholders: { [p: string]: number }): void {
            throw Error('Not Implemented Yet')
        }

        async compile(): Promise<void> {
            // if (!this.descriptor) throw new Error('Descriptor is not loaded');
            //
            // let descriptor = this.descriptor;
            //
            // this.compileKernel();
            // this.rawArray = new Float32Array(descriptor.memory_layout.total_size);
            // this.variableArrays = new Map();
            //
            // for (let name in descriptor.memory_layout.allocations) {
            //     let alloc = descriptor.memory_layout.allocations[name];
            //     this.variableArrays.set(name, new Float32Array(this.rawArray.buffer, alloc.offset * Float32Array.BYTES_PER_ELEMENT, alloc.size));
            // }
        }

        private compileKernel(): void {
            if (!this.descriptor) throw new Error('Descriptor is not loaded');

            let dnn_fallback_kernel: any = null;
            eval(this.descriptor.kernel_source);

            this.kernelObj = dnn_fallback_kernel;
        }

        async loadWeights(weightsData: Uint8Array): Promise<void> {
            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            if (!this.rawArray) throw new Error('Raw array is not loaded');

            // when weight format becomes not flat array (such as using quantization), the interface should be changed
            let decoder = get_weight_decoder(this.descriptor.weight_encoding);
            this.rawArray.set(await decoder.decode(weightsData, this.descriptor.memory_layout));
        }

        async run(): Promise<void> {
            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            if (!this.variableArrays) throw new Error('Variable map is not initialized');
            if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');

            let descriptor = this.descriptor;
            let variableArrays = this.variableArrays;

            let run_entry_date = Date.now();
            let last_progress_date = Date.now();//in milliseconds
            for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                let current_date = Date.now();
                if (current_date - last_progress_date >= 1000) {
                    let elapsed_ms = current_date - run_entry_date;
                    console.log(`Processed ${i}/${this.descriptor.exec_infos.length} kernels in ${elapsed_ms} ms`);
                    last_progress_date = current_date;
                    await this.wait_to_display();
                }
                let exec_info = this.descriptor.exec_infos[i];
                let input_arrays = exec_info.inputs.map((name) => variableArrays.get(name));
                let output_arrays = exec_info.outputs.map((name) => variableArrays.get(name));
                this.kernelObj[exec_info.entry_func_name](input_arrays, output_arrays, exec_info.call_option);
            }
            console.log(`Processed ${this.descriptor.exec_infos.length}/${this.descriptor.exec_infos.length} kernels in ${Date.now() - run_entry_date} ms`);
        }

        async wait_to_display() {
            // let console.log to be displayed, and prevent freeze
            return new Promise(function (resolve) {
                setTimeout(resolve, 10);
            });
        }

        async getInputViews(): Promise<SymbolicFloat32Array[]> {
            // if (!this.descriptor) throw new Error('Descriptor is not loaded');
            // if (!this.variableArrays) throw new Error('Variable map is not initialized');
            // if (this.inputViews) return this.inputViews;
            //
            // let variableArrays = this.variableArrays;
            // let views = this.descriptor.inputs.map((name) => variableArrays.get(name)!);
            // this.inputViews = views;
            //
            // return views;
            return [];
        }

        async getOutputViews(): Promise<SymbolicFloat32Array[]> {
            // if (!this.descriptor) throw new Error('Descriptor is not loaded');
            // if (!this.variableArrays) throw new Error('Variable map is not initialized');
            // if (this.outputViews) return this.outputViews;
            //
            // let variableArrays = this.variableArrays;
            // let views = this.descriptor.outputs.map((name) => variableArrays.get(name)!);
            // this.outputViews = views;
            //
            // return views;
            return [];
        }
    }
}
