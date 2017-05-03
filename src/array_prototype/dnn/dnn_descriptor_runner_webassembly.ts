/// <reference path="../webgpu_handler.ts" />
/// <reference path="./dnn_descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />

declare var Module;

namespace WebDNN {
    export class DNNDescriptorRunnerWebassembly implements DNNDescriptorRunner {
        private inputViews: Float32Array[];
        private outputViews: Float32Array[];

        constructor(public descriptor: DNNDescriptorWebassembly) {

        }

        async compile() {
            Module._init();
        }

        async loadWeights(weightsData: Uint8Array) {
            let decoder = get_weight_decoder(this.descriptor.weight_encoding);
            let weight_offset = Module._get_weight_buffer();
            let weight_buf = new Float32Array(Module.buffer, weight_offset, this.descriptor.weight_allocation.total_size);
            weight_buf.set(await decoder.decode(weightsData, this.descriptor.weight_allocation));
        }

        async getInputViews(): Promise<Float32Array[]> {
            let views: Float32Array[] = [];
            for (let i = 0; i < this.descriptor.inputs.length; i++) {
                let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.inputs[i]];
                views.push(new Float32Array(var_alloc.size));
            }
            this.inputViews = views;
            return views;
        }

        async getOutputViews(): Promise<Float32Array[]> {
            let views: Float32Array[] = [];
            for (let i = 0; i < this.descriptor.outputs.length; i++) {
                let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.outputs[i]];
                views.push(new Float32Array(var_alloc.size));
            }
            this.outputViews = views;
            return views;
        }

        async run(): Promise<void> {
            //set input to GPU
            let data_offset = Module._get_data_buffer();
            let data_buf = new Float32Array(Module.buffer, data_offset, this.descriptor.variable_allocation.total_size);
            for (let i = 0; i < this.descriptor.inputs.length; i++) {
                let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.inputs[i]];
                data_buf.set(this.inputViews[i], var_alloc.offset);
            }

            //execute kernels
            Module._run();

            // get output from GPU
            for (let i = 0; i < this.descriptor.outputs.length; i++) {
                let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.outputs[i]];
                let data_buf_view = new Float32Array(data_buf.buffer, data_buf.byteOffset + var_alloc.offset * Float32Array.BYTES_PER_ELEMENT, var_alloc.size);
                this.outputViews[i].set(data_buf_view);
            }
        }
    }

    export interface DNNDescriptorWebassembly {
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
        weight_encoding: string;
    }
}
