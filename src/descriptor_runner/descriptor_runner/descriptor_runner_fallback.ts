/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import get_weight_decoder from "../decoder/get_weight_decoder";
import webdnnFetch, { readArrayBufferProgressively } from "../fetch"
import { GraphDescriptorFallback } from "../graph_descriptor/graph_descriptor_fallback";
import { Allocation, ResolvedAllocation } from "../graph_descriptor/memory_layout";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import { BackendName } from "../webdnn";
import { DescriptorRunner } from "./descriptor_runner";

/**
 * @private
 */
function wait(duration: number = 10) {
    // let console.log to be displayed, and prevent freeze
    return new Promise(resolve => setTimeout(resolve, duration));
}

/**
 * @protected
 */
export default class DescriptorRunnerFallback extends DescriptorRunner<GraphDescriptorFallback> {
    readonly backendName: BackendName = 'fallback';

    private kernelObj: any;
    private variableMap: Map<string, Float32Array> | null;
    private inputViews: SymbolicFloat32Array[] | null;
    private outputViews: SymbolicFloat32Array[] | null;
    private staticBuffer: Float32Array | null;
    private dynamicBuffer: Float32Array | null;

    static checkAvailability() {
        return true;
    }

    async init(): Promise<void> {
        //nothing to do
    }

    async load(directory: string, progressCallback?: (loaded: number, total: number) => any) {
        let [descriptor, weightRawArray] = await Promise.all([
            webdnnFetch(`${directory}/graph_${this.backendName}.json`, {ignoreCache: this.ignoreCache, progressCallback: progressCallback})
                .then(res => res.json() as Promise<GraphDescriptorFallback>),

            webdnnFetch(`${directory}/weight_${this.backendName}.bin`, {ignoreCache: this.ignoreCache})
                .then(res => readArrayBufferProgressively(res, progressCallback))
        ]);

        this.setDescriptor(descriptor);

        await this.compile();
        await this.initializeStaticBuffer(weightRawArray);
        if (this.placeholderContext && this.placeholderContext.isResolved) await this.initializeDynamicBuffer();
    }

    private setDescriptor(descriptor: GraphDescriptorFallback) {
        this.descriptor = descriptor;

        // reset
        this.placeholderContext = new PlaceholderContext();
        this.placeholderContext.update(descriptor.placeholders);
        this.kernelObj = null;
        this.variableMap = null;
        this.outputViews = null;
        this.inputViews = null;
        this.staticBuffer = null;
        this.dynamicBuffer = null;
    }

    private async compile(): Promise<void> {
        if (!this.descriptor) throw new Error('Descriptor is not loaded');

        let dnn_fallback_kernel: any = null;
        eval(this.descriptor.kernel_source);

        this.kernelObj = dnn_fallback_kernel;
    }

    private async initializeStaticBuffer(weightRawArray: ArrayBuffer) {
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        let descriptor = this.descriptor;

        let staticBuffer = new Float32Array(descriptor.memory_layout.static.size);
        this.staticBuffer = staticBuffer;

        let variableMap = this.variableMap || new Map();
        this.variableMap = variableMap;

        Object.entries(descriptor.memory_layout.static.allocations)
            .forEach(([name, allocation]: [string, ResolvedAllocation]) => {
                variableMap.set(
                    name,
                    new Float32Array(
                        staticBuffer.buffer,
                        allocation.offset * Float32Array.BYTES_PER_ELEMENT,
                        allocation.size
                    )
                );
            });

        let decoder = get_weight_decoder(this.descriptor.weight_encoding);
        staticBuffer.set(await decoder.decode(new Uint8Array(weightRawArray)));

        (await this.getInputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(staticBuffer.buffer));

        (await this.getOutputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(staticBuffer.buffer));
    }

    private async initializeDynamicBuffer() {
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');
        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;

        let dynamicBuffer = new Float32Array(placeholderContext.resolve(descriptor.memory_layout.dynamic.size));
        this.dynamicBuffer = dynamicBuffer;

        let variableMap = this.variableMap || new Map();
        this.variableMap = variableMap;

        Object.entries(descriptor.memory_layout.dynamic.allocations)
            .forEach(([name, allocation]: [string, Allocation]) => {
                variableMap.set(
                    name,
                    new Float32Array(
                        dynamicBuffer.buffer,
                        placeholderContext.resolve(allocation.offset) * Float32Array.BYTES_PER_ELEMENT,
                        placeholderContext.resolve(allocation.size)
                    )
                );
            });

        (await this.getInputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(dynamicBuffer.buffer));

        (await this.getOutputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(dynamicBuffer.buffer));
    }

    async setPlaceholderValue(values: { [key: string]: number; }) {
        if (!this.placeholderContext) throw new Error('placeholderContext is not initialized');
        let placeholderContext = this.placeholderContext;

        placeholderContext.update(values);
        if (!placeholderContext.isResolved) return;

        await this.initializeDynamicBuffer();
    }

    async run(): Promise<void> {
        if (this._running) throw new Error('Calling another run() while running.');
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('placeholderContext is not initialized');
        if (!this.variableMap) throw new Error('Variable map is not initialized');
        if (!this.staticBuffer) throw new Error('StaticBuffer map is not initialized');
        if (!this.dynamicBuffer) throw new Error('DynamicBuffer map is not initialized');
        if (!this.inputViews || !this.outputViews) throw new Error('getInputViews() and getOutputViews() must be called prior to run');

        let variableMap = this.variableMap;
        let placeholderContext = this.placeholderContext;
        let executionInfos = this.descriptor.exec_infos
            .map(executionInfo => placeholderContext.resolve(executionInfo));

        let startDate = Date.now();
        let lastDate = Date.now();

        this._running = true;
        for (let i = 0; i < executionInfos.length; i++) {
            let currentDate = Date.now();
            if (currentDate - lastDate >= 1000) {
                console.log(`Processed ${i}/${executionInfos.length} kernels in ${currentDate - startDate} ms`);
                lastDate = currentDate;

                await wait();
            }

            let executionInfo = executionInfos[i];
            let inputs = executionInfo.inputs.map((name) => variableMap.get(name));
            let outputs = executionInfo.outputs.map((name) => variableMap.get(name));
            this.kernelObj[executionInfo.entry_func_name](inputs, outputs, executionInfo.call_option);
        }
        console.log(`Processed ${executionInfos.length}/${executionInfos.length} kernels in ${Date.now() - startDate} ms`);
        this._running = false;
    }

    getInputViews() {
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

    getOutputViews() {
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
}
