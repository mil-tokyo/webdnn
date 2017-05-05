/// <reference path="../webgpu_handler.ts" />
/// <reference path="./dnn_descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />

namespace WebDNN {
    export class DNNDescriptorRunnerWebassembly implements DNNDescriptorRunner {
        private inputViews: Float32Array[];
        private outputViews: Float32Array[];
        private worker: Worker;
        public descriptor: DNNDescriptorWebassembly;
        public ignoreCache: boolean = false;
        public backend: string = 'webassembly';

        constructor() {

        }

        async load(directory: string) {
            let graph_url = `${directory}/graph_${this.backend}.json`;
            if (this.ignoreCache) {
                graph_url += '?t=' + Date.now();
            }
            this.descriptor = await (await fetch(graph_url)).json();
            await this.compile();

            let weight_url = `${directory}/weight_${this.backend}.bin`;
            if (this.ignoreCache) {
                weight_url += '?t=' + Date.now();
            }
            let weights_data_ab = await (await fetch(weight_url)).arrayBuffer();
            await this.loadWeights(new Uint8Array(weights_data_ab));
        }

        setDescriptor(descriptor: DNNDescriptorWebassembly) {
            this.descriptor = descriptor;
        }

        compile(): Promise<void> {
            this.worker = new Worker(this.descriptor.entry_js_path);
            let promise = new Promise<void>((resolve, reject) => {
                this.worker.onmessage = (event) => {
                    console.log('init_response', event.data);
                    resolve();
                };

                this.worker.postMessage({ type: 'init' });
            });

            return promise;
        }

        async loadWeights(weightsData: Uint8Array) {
            let decoder = get_weight_decoder(this.descriptor.weight_encoding);
            let weight_data = await decoder.decode(weightsData, this.descriptor.weight_allocation);
            let promise = new Promise<void>((resolve, reject) => {
                this.worker.onmessage = (event) => {
                    console.log('weight_response', event.data);
                    resolve();
                };

                this.worker.postMessage({ type: 'weight', data: weight_data });
            });

            return promise;
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
            let promise = new Promise<void>((resolve, reject) => {
                // TODO: better way not to generate function on every run
                this.worker.onmessage = (event) => {
                    console.log('received output');
                    for (let i = 0; i < event.data.length; i++) {
                        this.outputViews[i].set(event.data[i]);
                    }
                    resolve();
                };

                let inputs: any = [];
                for (let i = 0; i < this.descriptor.inputs.length; i++) {
                    let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.inputs[i]];
                    inputs.push({ offset: var_alloc.offset, size: var_alloc.size, data: this.inputViews[i] });
                }
                let outputs: any = [];
                for (let i = 0; i < this.descriptor.outputs.length; i++) {
                    let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.outputs[i]];
                    outputs.push({ offset: var_alloc.offset, size: var_alloc.size });
                }
                this.worker.postMessage({ type: 'run', inputs: inputs, outputs: outputs });
            });

            return promise;
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
        entry_js_path: string;
    }
}
