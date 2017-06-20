/// <reference path="../webgpu_handler.ts" />
/// <reference path="./descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />
/// <reference path="../fetch.ts" />
/// <reference path="../graph_descriptor/graph_descriptor_webassembly.ts" />

declare let WebAssembly;

namespace WebDNN {
    export class DescriptorRunnerWebassembly extends DescriptorRunner<GraphDescriptorWebassembly> {
        readonly backendName = 'webassembly';

        inputViews: Float32Array[] | null;
        outputViews: Float32Array[] | null;
        worker: Worker | null;
        worker_entry_js_path;
        worker_promise_reject_func: any = null;
        worker_initial_error: any = null;

        constructor(option?: any) {
            super();
            if (typeof Worker === 'undefined') {
                throw new Error('WebWorker is needed for WebAssembly backend');
            }
            if (typeof WebAssembly !== 'object') {
                console.warn('WebAssembly is not supported on this browser, trying to use asm.js code');
            }
        }

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

            // for browsers which does not support wasm, try asm.js code
            let kernel_backend = typeof WebAssembly === 'object' ? 'webassembly' : 'asmjs';
            let worker_entry_js_path = `${directory}/kernels_${kernel_backend}.js`;
            if (this.ignoreCache) {
                worker_entry_js_path += '?t=' + Date.now();
            }
            worker_entry_js_path = transformUrl(worker_entry_js_path);
            this.worker_entry_js_path = worker_entry_js_path;

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

        compile(): Promise<void> {
            let worker = new Worker(this.worker_entry_js_path);
            worker.onerror = (event) => {
                console.error(event);
                // console.error('Worker Exception: ' + event.message);
                if (this.worker_promise_reject_func) {
                    this.worker_promise_reject_func(event);
                } else {
                    this.worker_initial_error = event;
                }
            };
            let promise = new Promise<void>((resolve, reject) => {
                // occurs when this.worker_entry_js_path is 404
                if (this.worker_initial_error) return reject(this.worker_initial_error);

                this.worker_promise_reject_func = reject;
                worker.onmessage = (event) => {
                    if (event.data === 0) {
                        resolve();
                    } else {
                        console.error(event.data);
                        worker.terminate();
                        reject(new Error(event.data));
                    }
                };
            });

            this.worker = worker;
            return promise;
        }

        async loadWeights(weightsData: Uint8Array) {
            if (!this.descriptor) throw new Error('Descriptor is not loaded');
            if (!this.worker) throw new Error('Worker is not initialized');

            let decoder = get_weight_decoder(this.descriptor.weight_encoding);
            let weight_data = await decoder.decode(weightsData, this.descriptor.memory_layout);
            let worker = this.worker;

            let promise = new Promise<void>((resolve, reject) => {
                this.worker_promise_reject_func = reject;
                worker.onmessage = (event) => {
                    if (event.data === 0) {
                        resolve();
                    } else {
                        console.log(event.data);
                        worker.terminate();
                        reject(new Error(event.data));
                    }
                };

                worker.postMessage({type: 'weight', data: weight_data});
            });

            return promise;
        }

        async getInputViews(): Promise<SymbolicFloat32Array[]> {
            // if (this.inputViews) return this.inputViews;
            //
            // if (!this.descriptor) throw new Error('Descriptor is not loaded');
            //
            // let views: Float32Array[] = [];
            // for (let i = 0; i < this.descriptor.inputs.length; i++) {
            //     let var_alloc = this.descriptor.memory_layout.allocations[this.descriptor.inputs[i]];
            //     views.push(new Float32Array(var_alloc.size));
            // }
            // this.inputViews = views;
            // return views;
            return []
        }

        async getOutputViews(): Promise<SymbolicFloat32Array[]> {
            // if (this.outputViews) return this.outputViews;
            //
            // if (!this.descriptor) throw new Error('Descriptor is not loaded');
            //
            // let views: Float32Array[] = [];
            // for (let i = 0; i < this.descriptor.outputs.length; i++) {
            //     let var_alloc = this.descriptor.memory_layout.allocations[this.descriptor.outputs[i]];
            //     views.push(new Float32Array(var_alloc.size));
            // }
            // this.outputViews = views;
            // return views;
            return []
        }

        async run(): Promise<void> {
            // if (!this.descriptor) throw new Error('Descriptor is not loaded');
            // if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');
            // if (!this.worker) throw new Error('Worker is not initialized');
            //
            // let descriptor = this.descriptor;
            // let worker = this.worker;
            // let inputViews = this.inputViews;
            // let outputViews = this.outputViews;
            //
            // let promise = new Promise<void>((resolve, reject) => {
            //     // TODO: better way not to generate function on every run
            //     this.worker_promise_reject_func = reject;
            //     worker.onmessage = (event) => {
            //         if (Array.isArray(event.data)) {
            //             for (let i = 0; i < event.data.length; i++) {
            //                 outputViews[i].set(event.data[i]);
            //             }
            //             resolve();
            //         } else {
            //             console.log(event.data);
            //             worker.terminate();
            //             reject(new Error(event.data));
            //         }
            //     };
            //
            //     let inputs: any = [];
            //     for (let i = 0; i < descriptor.inputs.length; i++) {
            //         let var_alloc = descriptor.memory_layout.allocations[descriptor.inputs[i]];
            //         inputs.push({offset: var_alloc.offset, size: var_alloc.size, data: inputViews[i]});
            //     }
            //
            //     let outputs: any = [];
            //     for (let i = 0; i < descriptor.outputs.length; i++) {
            //         let var_alloc = descriptor.memory_layout.allocations[descriptor.outputs[i]];
            //         outputs.push({offset: var_alloc.offset, size: var_alloc.size});
            //     }
            //
            //     worker.postMessage({type: 'run', inputs: inputs, outputs: outputs});
            // });
            //
            // return promise;
        }
    }
}
