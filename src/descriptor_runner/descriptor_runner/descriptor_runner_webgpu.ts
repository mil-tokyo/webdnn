/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import BufferWebGPU from "../buffer/buffer_webgpu";
import getWeightDecoder from "../decoder/get_weight_decoder";
import webdnnFetch, { readArrayBufferProgressively } from "../fetch";
import { GraphDescriptorWebGPU, GraphDescriptorWebGPUExecInfos } from "../graph_descriptor/graph_descriptor_webgpu";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import * as localforage_ from "../third/localforage.nopromises.min";
import { BackendName, getConfiguration } from "../webdnn";
import WebGPUHandler, { IS_WEBGPU_SUPPORTED } from "../webgpu_handler";
import { DescriptorRunner } from "./descriptor_runner";

/**
 * @private
 */
const localforage = localforage_.default;

/**
 * Check this device is iOS devices or not.
 * @private
 */
const IS_IOS = navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad');

/**
 * DescriptorRunner for WebGPU
 * @protected
 */
export default class DescriptorRunnerWebGPU extends DescriptorRunner<GraphDescriptorWebGPU, ArrayBuffer> {
    /**
     * backend name
     * @type {string}
     */
    readonly backendName: BackendName = 'webgpu';

    /**
     * WebGPU Handler
     */
    private webgpuHandler: WebGPUHandler;

    /**
     * Static buffer, whose size and layout can be determined in compile time.
     */
    private staticBuffer: BufferWebGPU | null;

    /**
     * Buffers whose size and layout cannot be determined without runtime information like image size (if it's dynamic).
     */
    private dynamicBuffer: BufferWebGPU | null;

    /**
     * Buffers which contains metadata shared in each GPU kernel thread (ex. hyper parameters).
     */
    private metaBuffers: BufferWebGPU[] | null;

    /**
     * Input views
     */
    private inputViews: SymbolicFloat32Array[] | null;

    /**
     * Output views
     */
    private outputViews: SymbolicFloat32Array[] | null;

    /**
     * Execution information such as each kernel size, input and output buffers, etc.
     */
    private executionInfos: GraphDescriptorWebGPUExecInfos[] | null;

    /**
     * Return `true` if this backend is available in this environment.
     * @returns {boolean}
     */
    static checkAvailability() {
        return IS_WEBGPU_SUPPORTED;
    }

    /**
     * Initialize descriptor runner asynchronously
     * @returns {Promise<void>} Promise object which is resolved when the initialization finished.
     */
    async init() {
        this.webgpuHandler = WebGPUHandler.getInstance();

        await this.checkIncompatibleGPU();
    }

    /**
     * Check whether current GPU is supported or not. If it's not supported, an error is thrown.
     * @returns {Promise<void>}
     */
    private async checkIncompatibleGPU() {
        /**
         * It is reported that AMD GPU crashes when performing sgemm (matrix multiplication).
         * Until this problem is solved, blocking WebGPU backend in the environment is needed.
         * API in WebGPU does not directly gives hardware information, so trying to determine hardware heuristically.
         *
         * Criteria: thread_execution_width == 32 is required
         * (on AMD FirePro D500, thread_execution_width == 64)
         *
         * @see https://github.com/mil-tokyo/webdnn/issues/286
         */
        this.webgpuHandler.loadKernel(`
#include <metal_stdlib>
using namespace metal;
        kernel void check_compatibility(
            device uint *A[[buffer(0)]],
            uint global_index[[thread_position_in_grid]],
            uint thread_execution_width[[thread_execution_width]]
        ){
            if (global_index == 0) {
                A[0] = thread_execution_width;
            }
        }`, 'basic');
        let buffer = this.webgpuHandler.createBuffer(new Uint32Array(1));
        await this.webgpuHandler.executeSinglePipelineState(
            'basic.check_compatibility',
            {width: 1, height: 1, depth: 1},
            {width: 1, height: 1, depth: 1},
            [buffer],
            true
        );
        let threadExecutionWidth = (new Uint32Array(buffer.contents))[0];
        if (threadExecutionWidth != 32) {
            throw new Error(`Sorry, this GPU does not compatible with WebGPU (thread_execution_width == ${threadExecutionWidth}. See checkIncompatibleGPU method of https://github.com/mil-tokyo/webdnn/blob/master/src/descriptor_runner/descriptor_runner/descriptor_runner_webgpu.ts`);
        }
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
    async fetchDescriptor(directory: string): Promise<GraphDescriptorWebGPU> {
        let res = await webdnnFetch(`${directory}/graph_${this.backendName}.json`);
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
        let res = await webdnnFetch(`${directory}/weight_${this.backendName}.bin`);
        return readArrayBufferProgressively(res, progressCallback);
    }

    /**
     * Load cached descriptor from WebStorage
     * @protected
     */
    async restoreCachedDescriptor(directory: string): Promise<GraphDescriptorWebGPU | null> {
        return localforage.getItem<GraphDescriptorWebGPU>(`${directory}_${this.backendName}_descriptor`).catch(() => null);
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
    async saveCache(directory: string, descriptor: GraphDescriptorWebGPU, parameters: ArrayBuffer): Promise<void> {
        await Promise.all([
            localforage.setItem(`${directory}_${this.backendName}_descriptor`, descriptor),
            localforage.setItem(`${directory}_${this.backendName}_parameters`, parameters)
        ]);
    };

    async setDescriptorAndParameters(descriptor: GraphDescriptorWebGPU, parameter: ArrayBuffer) {
        this.descriptor = descriptor;

        //reset all datum depend on old descriptor
        this.staticBuffer = null;
        this.dynamicBuffer = null;
        this.metaBuffers = null;
        this.placeholderContext = new PlaceholderContext(descriptor.placeholders);
        this.executionInfos = descriptor.exec_infos;

        //compile kernels
        this.webgpuHandler.loadKernel(this.descriptor.kernel_source, 'descriptor');

        await this.initializeStaticBuffer(parameter);
        await this.initializeMetaBuffers();

        await this.setPlaceholderValue({
            '__MAX_THREADS_PER_THREADGROUP__': IS_IOS ? 512 : 1024
        });
        if (this.placeholderContext && this.placeholderContext.isResolved) await this.initializeDynamicBuffer();
    }


    /**
     * Initialize static buffers, whose size and position can be determined in compile time.
     *
     * @param {ArrayBuffer} weightRawArray constant weight buffer
     * @returns {Promise<void>}
     */
    private async initializeStaticBuffer(weightRawArray: ArrayBuffer) {
        if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
        let descriptor = this.descriptor;

        let staticBuffer = new BufferWebGPU(descriptor.memory_layout.static.size * Float32Array.BYTES_PER_ELEMENT);
        this.staticBuffer = staticBuffer;

        let decoder = getWeightDecoder(descriptor.weight_encoding);
        await staticBuffer.write(await decoder.decode(new Uint8Array(weightRawArray)));

        (await this.getInputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(staticBuffer.bufferView.buffer));

        (await this.getOutputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(staticBuffer.bufferView.buffer));
    }

    /**
     * Initialize meta buffers, which contains metadata shared in each GPU kernel thread (ex. hyper parameters).
     * @returns {Promise<void>}
     */
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

    /**
     * Initialize dynamic buffers, whose size and position cannot be determined without runtime-information such as input image size
     * (if it's dynamic).
     * When all placeholder is resolved, this method is automatically called.
     *
     * @returns {Promise<void>}
     */
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

    /**
     * Set actual value into placeholder. If all placeholder is resolved,
     * [[DescriptorRunnerWebGPU#initializeDynamicBuffer|`initializeDynamicBuffer()`]] is automatically called.
     *
     * @param values mapping object of placeholder name and value
     * @returns {Promise<void>}
     */
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

    /**
     * Get input [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]] object
     *
     * @returns array of input [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]]
     */
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

    /**
     * Get output [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]] object
     *
     * @returns array of output [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]]
     */
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

    /**
     * Run descriptor. You must call [[webdnn.DescriptorRunner.getInputViews|`getInputViews`]] and
     * [[webdnn.DescriptorRunner.getOutputViews|`getOutputViews`]] before calling this function.
     */
    async run(): Promise<void> {
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

        if (getConfiguration('DEBUG', false)) {
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

            return complete_promise!;//wait to finish final kernel
        }

        // this._running = false;
    }
}
