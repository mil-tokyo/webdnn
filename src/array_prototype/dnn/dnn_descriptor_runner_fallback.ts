namespace WebDNN {
    export class DNNDescriptorRunnerFallback implements DNNDescriptorRunner {
        kernelObj: any;
        rawWeightArray: Float32Array;
        weightArrays: Map<string, Float32Array>;
        variableArrays: Map<string, Float32Array>;

        constructor(public descriptor: DNNDescriptorFallback) {
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

        async loadWeights(weightsData: Float32Array): Promise<void> {
            // when weight format becomes not flat array (such as using quantization), the interface should be changed
            this.rawWeightArray.set(weightsData);
        }

        async run(): Promise<void> {
            let last_progress_date = Date.now();//in milliseconds
            for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
                let current_date = Date.now();
                if (current_date - last_progress_date > 1000) {
                    console.log('Processed ' + i + ' kernels at' + new Date());
                    last_progress_date = current_date;
                    await this.wait_to_display();
                }
                let exec_info = this.descriptor.exec_infos[i];
                let input_arrays = exec_info.inputs.map((name) => this.variableArrays.get(name));
                let output_arrays = exec_info.outputs.map((name) => this.variableArrays.get(name));
                let weight_arrays = exec_info.weights.map((name) => this.weightArrays.get(name));
                this.kernelObj[exec_info.entry_func_name](input_arrays, output_arrays, weight_arrays, exec_info.call_option);
            }
        }

        async wait_to_display() {
            return new Promise(function (resolve, reject) {
                setTimeout(resolve, 10);
            });
        }

        async getInputViews(): Promise<Float32Array[]> {
            let views = this.descriptor.inputs.map((name) => this.variableArrays.get(name)!);
            return views;
        }

        async getOutputViews(): Promise<Float32Array[]> {
            let views = this.descriptor.outputs.map((name) => this.variableArrays.get(name)!);
            return views;
        }
    }

    export interface DNNDescriptorFallback {
        kernel_source: string;
        exec_infos: DNNDescriptorFallbackExecInfo[];
        weight_allocation: {
            total_size: number;
            allocation: { [index: string]: { name: string, offset: number, size: number } }
        };
        variable_allocation: {
            total_size: number;
            allocation: { [index: string]: { name: string, offset: number, size: number } }
        };
        inputs: string[];
        outputs: string[];
        batch_size: number;
    }

    export interface DNNDescriptorFallbackExecInfo {
        entry_func_name: string;
        inputs: string[];
        outputs: string[];
        weights: string[];
        call_option: any;
    }
}
