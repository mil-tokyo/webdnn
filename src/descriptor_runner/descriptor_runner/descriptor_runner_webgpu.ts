/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import BufferWebGPU from "../buffer/buffer_webgpu";
import get_weight_decoder from "../decoder/get_weight_decoder";
import webdnnFetch, { readArrayBufferProgressively } from "../fetch";
import { GraphDescriptorWebGPU, GraphDescriptorWebGPUExecInfos } from "../graph_descriptor/graph_descriptor_webgpu";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import { isDebugMode } from "../webdnn";
import WebGPUHandler, { IS_WEBGPU_SUPPORTED } from "../webgpu_handler";
import { DescriptorRunner } from "./descriptor_runner";

/**
 * @private
 */
const IS_IOS = navigator.userAgent.includes('iPhone');

/**
 * @protected
 */
export default class DescriptorRunnerWebGPU extends DescriptorRunner<GraphDescriptorWebGPU> {
    readonly backendName = 'webgpu';

    private webgpuHandler: WebGPUHandler;
    private shaderLanguage: string;

    private staticBuffer: BufferWebGPU | null;
    private dynamicBuffer: BufferWebGPU | null;
    private metaBuffers: BufferWebGPU[] | null;

    private inputViews: SymbolicFloat32Array[] | null;
    private outputViews: SymbolicFloat32Array[] | null;

    private executionInfos: GraphDescriptorWebGPUExecInfos[] | null;

    static checkAvailability() {
        return IS_WEBGPU_SUPPORTED;
    }

    //noinspection JSUnusedLocalSymbols
    constructor(option?: any) {
        super();
    }

    async init() {
        if (!DescriptorRunnerWebGPU.checkAvailability()) throw Error('WebGPU backend is not supported in this browser.');

        // initialize webgpu, build kernels
        this.shaderLanguage = 'metal';
        this.webgpuHandler = new WebGPUHandler();
        BufferWebGPU.init(this.webgpuHandler);

        this.initializeBasicKernels();
    }

    private initializeBasicKernels() {
        this.webgpuHandler.loadKernel('kernel void sync(){}', 'basic');
    }

    async load(directory: string, progressCallback?: (loaded: number, total: number) => any) {
        let [descriptor, weightRawArray] = await Promise.all([
            webdnnFetch(`${directory}/graph_${this.backendName}.json`, {ignoreCache: this.ignoreCache})
                .then(res => res.json() as Promise<GraphDescriptorWebGPU>),

            webdnnFetch(`${directory}/weight_${this.backendName}.bin`, {ignoreCache: this.ignoreCache})
                .then(res => readArrayBufferProgressively(res, progressCallback))
        ]);

        await this.setDescriptor(descriptor);
        await this.compile();
        await this.initializeStaticBuffer(weightRawArray);
        await this.initializeMetaBuffers();

        await this.setPlaceholderValue({
            '__MAX_THREADS_PER_THREADGROUP__': IS_IOS ? 512 : 512
        });
        if (this.placeholderContext && this.placeholderContext.isResolved) await this.initializeDynamicBuffer();
    }

    private async initializeStaticBuffer(weightRawArray: ArrayBuffer) {
        if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
        let descriptor = this.descriptor;

        let staticBuffer = new BufferWebGPU(descriptor.memory_layout.static.size * Float32Array.BYTES_PER_ELEMENT);
        this.staticBuffer = staticBuffer;

        let decoder = get_weight_decoder(descriptor.weight_encoding);
        await staticBuffer.write(await decoder.decode(new Uint8Array(weightRawArray)));

        (await this.getInputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(staticBuffer.bufferView.buffer));

        (await this.getOutputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(staticBuffer.bufferView.buffer));
    }

    private async initializeMetaBuffers() {
        if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");

        this.metaBuffers = await Promise.all<BufferWebGPU>(
            this.descriptor.exec_infos.map(async executionInfo => {
                let buffer = new BufferWebGPU(executionInfo.meta_buffer.length * Int32Array.BYTES_PER_ELEMENT);
                await buffer.write(new Uint8Array(executionInfo.meta_buffer));

                return buffer;
            })
        );
    }

    private async initializeDynamicBuffer() {
        if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
        if (!this.placeholderContext) throw Error("PlaceholderContext is not initialized.");
        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;

        let dynamicBufferSize = placeholderContext.resolve(descriptor.memory_layout.dynamic.size);
        let dynamicBuffer = new BufferWebGPU(dynamicBufferSize * Float32Array.BYTES_PER_ELEMENT);
        this.dynamicBuffer = dynamicBuffer;

        (await this.getInputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(dynamicBuffer.bufferView.buffer));

        (await this.getOutputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(dynamicBuffer.bufferView.buffer));
    }

    private async setDescriptor(descriptor: GraphDescriptorWebGPU) {
        this.descriptor = descriptor;

        //reset all datum depend on old descriptor
        this.staticBuffer = null;
        this.dynamicBuffer = null;
        this.metaBuffers = null;
        this.placeholderContext = new PlaceholderContext(descriptor.placeholders);
        this.executionInfos = descriptor.exec_infos;
    }

    private async compile() {
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

        await this.initializeDynamicBuffer();

        // resolve placeholders in execution info
        this.executionInfos = await Promise.all(
            descriptor.exec_infos.map(async (executionInfo, i) => {

                // resolve placeholders in meta buffer
                let bufferView = new Int32Array(metaBuffers[i].bufferView.buffer);
                for (let unresolved_value of executionInfo.unresolved_value_list) {
                    bufferView[unresolved_value.offset] = placeholderContext.resolve(unresolved_value.placeholder);
                }

                return placeholderContext.resolve(executionInfo);
            })
        );
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

    async run(): Promise<void> {
        if (this._running) throw new Error('Calling another run() while running.');
        if (!this.executionInfos) throw new Error('ExecutionInfos is not loaded');
        if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');
        if (!this.staticBuffer) throw new Error('StaticBuffer is not initialized');
        if (!this.dynamicBuffer) throw new Error('DynamicBuffer is not initialized');
        if (!this.metaBuffers) throw new Error('MetaBuffer is not initialized');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');
        if (!this.placeholderContext.isResolved) throw new Error(`Not all placeholders are resolved: ${this.placeholderContext}`);

        let staticBuffer = this.staticBuffer;
        let dynamicBuffer = this.dynamicBuffer;
        let metaBuffers = this.metaBuffers;

        this._running = true;
        if (isDebugMode()) {
            let records: any = [];
            let totalElapsedTime = 0;

            for (let i = 0; i < this.executionInfos.length; i++) {
                let exec_info = this.executionInfos[i];

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
            for (let i = 0; i < this.executionInfos.length; i++) {
                let exec_info = this.executionInfos[i];
                let is_last = i == this.executionInfos.length - 1;
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

        this._running = false;
    }
}
