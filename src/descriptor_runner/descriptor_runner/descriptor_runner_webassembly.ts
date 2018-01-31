/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import * as localforage from "localforage";
import get_weight_decoder from "../decoder/get_weight_decoder";
import webDNNFetch, { readArrayBufferProgressively, transformUrl } from "../fetch";
import { GraphDescriptorWebassembly } from "../graph_descriptor/graph_descriptor_webassembly";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import { BackendName } from "../webdnn";
import { DescriptorRunner } from "./descriptor_runner";

/**
 * @private
 */
declare let WebAssembly: any;

/**
 * @protected
 */
export default class DescriptorRunnerWebassembly extends DescriptorRunner<GraphDescriptorWebassembly, ArrayBuffer> {
    readonly backendName: BackendName = 'webassembly';

    private worker: Worker | null;
    private worker_entry_js_path;
    private worker_promise_reject_func: any = null;
    private worker_initial_error: any = null;
    private directory: string;

    static checkAvailability() {
        return 'Worker' in window;
    }

    constructor() {
        super();
        if (typeof Worker === 'undefined') throw new Error('WebWorker is needed for WebAssembly backend');
        if (typeof WebAssembly !== 'object') {
            console.warn('WebAssembly is not supported on this browser, trying to use asm.js code');
        }
    }

    init(): Promise<void> {
        if (!DescriptorRunnerWebassembly.checkAvailability()) throw Error('WebAssembly backend is not supported in this browser.');

        //nothing to do
        return Promise.resolve();
    }

    async setDescriptorAndParameters(descriptor: GraphDescriptorWebassembly, parameters: ArrayBuffer): Promise<void> {
        this.descriptor = descriptor;
        this.placeholderContext = new PlaceholderContext(this.descriptor!.placeholders);

        // for browsers which does not support wasm, try asm.js code
        let kernel_backend = typeof WebAssembly === 'object' ? 'webassembly' : 'asmjs';
        let worker_entry_js_path = `${this.directory}/kernels_${kernel_backend}.js`;
        worker_entry_js_path = transformUrl(worker_entry_js_path);
        this.worker_entry_js_path = worker_entry_js_path;

        await this.compile();

        await this.loadWeights(new Uint8Array(parameters));

        //assign buffer to input/output buffer view
        (await this.getInputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => {
                view.buffer = (new Float32Array(view.length)).buffer;
            });

        (await this.getOutputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => {
                view.buffer = (new Float32Array(view.length)).buffer;
            });
    }

    /**
     * Fetch graph descriptor from specified directory.
     *
     * @param directory directory where descriptor is contained.
     * You can also provide URL of other domain like this.
     *
     * ```javascript
     * await runner.load('://my.other.domain.com/my_model');
     * ```
     *
     * However sometimes it can't because of Cross-Origin-Resource-Security policy.
     *
     * @protected
     */
    async fetchDescriptor(directory: string): Promise<GraphDescriptorWebassembly> {
        this.directory = directory;
        let res = await webDNNFetch(`${directory}/graph_${this.backendName}.json`);
        return res.json();
    }

    /**
     * Fetch parameter files from specified directory.
     *
     * @param directory directory where descriptor is contained.
     * You can also provide URL of other domain like this.
     *
     * ```javascript
     * await runner.load('://my.other.domain.com/my_model');
     * ```
     *
     * However sometimes it can't because of Cross-Origin-Resource-Security policy.
     *
     * @param progressCallback callback which is called to notice the loading is progressing.
     * @protected
     */
    async fetchParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer> {
        let weight_url = `${directory}/weight_${this.backendName}.bin`;
        let weight_fetch = await webDNNFetch(weight_url);
        return readArrayBufferProgressively(weight_fetch, progressCallback);
    }

    /**
     * Load cached descriptor from WebStorage
     * @protected
     */
    async restoreCachedDescriptor(directory: string): Promise<GraphDescriptorWebassembly | null> {
        this.directory = directory;
        return localforage.getItem<GraphDescriptorWebassembly>(`${directory}_${this.backendName}_descriptor`).catch(() => null);
    }

    /**
     * Load cached descriptor from WebStorage
     * @protected
     */
    async restoreCachedParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer | null> {
        let parameter = await localforage.getItem<ArrayBuffer>(`${directory}_${this.backendName}_parameters`).catch(() => null);
        if (parameter && progressCallback) progressCallback(parameter.byteLength, parameter.byteLength);
        return parameter
    }

    /**
     * save cache
     */
    async saveCache(directory: string, descriptor: GraphDescriptorWebassembly, parameters: ArrayBuffer): Promise<void> {
        await Promise.all([
            localforage.setItem(`${directory}_${this.backendName}_descriptor`, descriptor),
            localforage.setItem(`${directory}_${this.backendName}_parameters`, parameters)
        ]);
    };

    async setPlaceholderValue(values: { [key: string]: number }): Promise<void> {
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized.');
        let placeholderContext = this.placeholderContext;

        placeholderContext.update(values);
        if (!placeholderContext.isResolved) return;

        if (!this.descriptor) throw new Error('Descriptor is not loaded');

        let descriptor = this.descriptor;
        let unresolvedValueLists = descriptor.unresolved_value_lists;

        let metaBufferFillList: number[] = [];
        for (let kernel_order = 0; kernel_order < unresolvedValueLists.length; kernel_order++) {
            let unresolvedValueList = unresolvedValueLists[kernel_order];
            unresolvedValueList.forEach((offset_placeholder) => {
                let resolved_value = placeholderContext.resolve(offset_placeholder.placeholder);
                metaBufferFillList.push(kernel_order, offset_placeholder.offset, resolved_value);
            });
        }

        (await this.getInputViews())
            .filter(view => view.isDynamic)
            .forEach(view => {
                view.buffer = (new Float32Array(view.length)).buffer;
            });

        (await this.getOutputViews())
            .filter(view => view.isDynamic)
            .forEach(view => {
                view.buffer = (new Float32Array(view.length)).buffer;
            });

        let dynamicBufferSize = this.placeholderContext.resolve(this.descriptor.memory_layout.dynamic.size);

        await this.setPlaceholderValueWorker(dynamicBufferSize, new Int32Array(metaBufferFillList));
    }

    private setPlaceholderValueWorker(dynamicBufferSize: number, metaBufferFillArray: Int32Array): Promise<void> {
        if (!this.worker) throw Error("Worker is not initialized");
        let worker = this.worker;
        return new Promise<void>((resolve, reject) => {
            worker.onmessage = (event) => {
                if (event.data === 0) {
                    resolve();
                } else {
                    console.log(event.data);
                    worker.terminate();
                    reject(new Error(event.data));
                }
            };

            worker.postMessage({type: 'set_dynamic_buffer', size: dynamicBufferSize, data: metaBufferFillArray});
        });
    }

    private compile(): Promise<void> {
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

    private async loadWeights(weightsData: Uint8Array) {
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.worker) throw new Error('Worker is not initialized');

        let decoder = get_weight_decoder(this.descriptor.weight_encoding);
        let weight_data = await decoder.decode(weightsData);
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

            worker.postMessage({type: 'weight', data: weight_data}, [weight_data.buffer]);
        });

        return promise;
    }

    getInputViews() {
        if (this.inputs) return this.inputs;

        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');

        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;

        this.inputs = descriptor.inputs.map(name => {
            let allocation = descriptor.memory_layout.static.allocations[name] || descriptor.memory_layout.dynamic.allocations[name];
            let view = new SymbolicFloat32Array(
                null,
                0,
                allocation.size,
                placeholderContext
            );

            return view;
        });

        return this.inputs;
    }

    getOutputViews() {
        if (this.outputs) return this.outputs;

        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');

        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;

        this.outputs = descriptor.outputs.map(name => {
            let allocation = descriptor.memory_layout.static.allocations[name] || descriptor.memory_layout.dynamic.allocations[name];
            let view = new SymbolicFloat32Array(
                null,
                0,
                allocation.size,
                placeholderContext
            );

            return view;
        });

        return this.outputs;
    }

    async run(): Promise<void> {
        // if (this._running) throw new Error('Calling another run() while running.');
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.worker) throw new Error('Worker is not initialized');
        if (!this.placeholderContext!.isResolved) throw new Error('Not all placeholder is resolved');

        let placeholderContext = this.placeholderContext!;
        let descriptor = this.descriptor;
        let worker = this.worker;

        let promise = new Promise<void>((resolve, reject) => {
            // TODO: better way not to generate function on every run
            this.worker_promise_reject_func = reject;
            worker.onmessage = (event) => {
                if (Array.isArray(event.data)) {
                    for (let i = 0; i < event.data.length; i++) {
                        this.outputs[i].set(event.data[i]);
                    }
                    resolve();
                } else {
                    console.log(event.data);
                    worker.terminate();
                    reject(new Error(event.data));
                }
            };

            let allocations = [descriptor.memory_layout.static.allocations, descriptor.memory_layout.dynamic.allocations];
            let inputs: any = [];
            for (let i = 0; i < descriptor.inputs.length; i++) {
                for (let allocation_space = 0; allocation_space < 2; allocation_space++) {
                    let var_alloc = allocations[allocation_space][descriptor.inputs[i]];
                    if (var_alloc) {
                        let symAb = this.inputs[i];
                        inputs.push({
                            space: allocation_space,
                            offset: placeholderContext.resolve(var_alloc.offset),
                            size: symAb.length,
                            data: symAb.toActual()
                        });
                        break;
                    }
                }
            }

            let outputs: any = [];
            for (let i = 0; i < descriptor.outputs.length; i++) {
                for (let allocation_space = 0; allocation_space < 2; allocation_space++) {
                    let var_alloc = allocations[allocation_space][descriptor.outputs[i]];
                    if (var_alloc) {
                        let symAb = this.outputs[i];
                        outputs.push({
                            space: allocation_space,
                            offset: placeholderContext.resolve(var_alloc.offset),
                            size: symAb.length
                        });
                        break;
                    }
                }
            }

            worker.postMessage({type: 'run', inputs: inputs, outputs: outputs});
        });

        return promise;
    }
}
