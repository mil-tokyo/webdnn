///<reference path="../fetch.ts" />
///<reference path="../graph_descriptor/graph_descriptor_fallback.ts" />

namespace WebDNN {
    export class DescriptorRunnerFallback implements DescriptorRunner {
        public descriptor: GraphDescriptorFallback;
        kernelObj: any;
        rawWeightArray: Float32Array;
        weightArrays: Map<string, Float32Array>;
        variableArrays: Map<string, Float32Array>;
        public ignoreCache: boolean = false;
        public backend: string = 'fallback';
        private inputViews: Float32Array[];
        private outputViews: Float32Array[];

        constructor() {
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
            let weights_data_ab = await readArrayBufferProgressively(await WebDNN.fetch(weight_url), progressCallback);
            await this.loadWeights(new Uint8Array(weights_data_ab));
        }

        setDescriptor(descriptor: GraphDescriptorFallback) {
            this.descriptor = descriptor;
        }

        async compile(): Promise<void> {
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

        private compileKernel(): void {
            var dnn_fallback_kernel: any;
            eval(this.descriptor.kernel_source);
            this.kernelObj = dnn_fallback_kernel;
        }

        async loadWeights(weightsData: Uint8Array): Promise<void> {
            // when weight format becomes not flat array (such as using quantization), the interface should be changed
            let decoder = get_weight_decoder(this.descriptor.weight_encoding);
            this.rawWeightArray.set(await decoder.decode(weightsData, this.descriptor.weight_allocation));
        }

        async run(): Promise<void> {
            if (!this.inputViews || !this.outputViews) {
                throw new Error('getInputViews and getOutputViews must be called prior to run');
            }
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

        async getInputViews(): Promise<Float32Array[]> {
            if (this.inputViews) {
                return this.inputViews;
            }
            let views = this.descriptor.inputs.map((name) => this.variableArrays.get(name)!);
            this.inputViews = views;
            return views;
        }

        async getOutputViews(): Promise<Float32Array[]> {
            if (this.outputViews) {
                return this.outputViews;
            }
            let views = this.descriptor.outputs.map((name) => this.variableArrays.get(name)!);
            this.outputViews = views;
            return views;
        }
    }
}
