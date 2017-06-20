declare namespace WebDNN {
    /**
     * Graph Descriptor
     */
    interface GraphDescriptor {
        /**
         * input variables' name
         */
        inputs: string[];
        /**
         * output variables' name
         */
        outputs: string[];
        /**
         * memory position table
         */
        memory_layout: MemoryLayout;
        /**
         * Encoding algorithm of weight binary data.
         */
        weight_encoding: string;
        /**
         * Placeholder dict
         */
        placeholders: {
            [key: string]: number;
        };
    }
}
declare namespace WebDNN {
    type Placeholder = {
        eval: string;
    };
    /**
     * PlaceholderContext manages the placeholders
     */
    class PlaceholderContext {
        private values;
        constructor(values?: {
            [key: string]: number | null;
        });
        readonly isResolved: boolean;
        update(values: {
            [key: string]: number | null;
        }): void;
        resolve(placeholder: number | Placeholder): any;
        toString(): string;
    }
}
declare namespace WebDNN {
    interface Allocation {
        name: string;
        offset: number | Placeholder;
        size: number | Placeholder;
    }
    interface ResolvedAllocation extends Allocation {
        offset: number;
        size: number;
    }
    interface MemoryLayout {
        'static': {
            size: number;
            allocations: {
                [index: string]: ResolvedAllocation;
            };
        };
        dynamic: {
            size: number | Placeholder;
            allocations: {
                [index: string]: Allocation;
            };
        };
    }
}
declare namespace WebDNN {
    abstract class SymbolicArrayBufferView<T extends ArrayBufferView> {
        protected arrayBuffer: ArrayBuffer;
        protected allocation: Allocation;
        protected placeholderContext?: PlaceholderContext;
        /**
         * Convert symbolic buffer view into actual buffer view.
         * If this buffer view is initialized based on placeholder offset or size and the placeholder is not resolved,
         * the error is thrown.
         */
        abstract toActual(): T;
        /**
         * Sets a value or an array of values.
         * @param array A typed or untyped array of values to set.
         * @param offset The index in the current array at which the values are to be written.
         */
        abstract set(array: ArrayLike<number>, offset?: number): any;
        constructor(allocation: Allocation, placeholderContext?: PlaceholderContext);
        setArrayBuffer(arrayBuffer: any): void;
        readonly isDynamic: boolean;
        readonly offset: any;
        readonly length: any;
    }
    class SymbolicFloat32Array extends SymbolicArrayBufferView<Float32Array> {
        toActual(): Float32Array;
        set(array: ArrayLike<number>, offset?: number): void;
    }
    class SymbolicInt32Array extends SymbolicArrayBufferView<Int32Array> {
        toActual(): Int32Array;
        set(array: ArrayLike<number>, offset?: number): void;
    }
}
declare namespace WebDNN {
    /**
     * `DescriptorRunner` executes computation based on `GraphDescriptor`.
     */
    abstract class DescriptorRunner<D extends GraphDescriptor> {
        readonly backendName: string;
        descriptor: D | null;
        placeholderContext: PlaceholderContext | null;
        ignoreCache: boolean;
        /**
         * Initialize this runner
         */
        abstract init(): Promise<void>;
        /**
         * Fetch descriptor from specified directory.
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
         */
        abstract load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;
        abstract setPlaceholderValue(placeholders: {
            [key: string]: number;
        }): void;
        /**
         * compile kernels.
         */
        abstract compile(): Promise<void>;
        /**
         * Run descriptor. You must call [[getInputViews]] and [[getOutputViews]] before calling this function.
         */
        abstract run(): Promise<void>;
        /**
         * Get input ArrayBufferView object
         */
        abstract getInputViews(): Promise<SymbolicFloat32Array[]>;
        /**
         * Get output ArrayBufferView object
         */
        abstract getOutputViews(): Promise<SymbolicFloat32Array[]>;
    }
}
declare namespace WebDNN {
    /**
     * Abstract buffer interface. Read/write transactions are regarded as asynchronous operation.
     */
    abstract class Buffer {
        byteLength: number;
        backed: string;
        constructor(byteLength: number, backed: string);
        /**
         * Write contents into specified position.
         * @param src contents souce buffer.
         * @param dst_offset position where contents are written on
         */
        abstract write(src: ArrayBufferView, dst_offset?: number): Promise<void>;
        /**
         * Read contents from specified position.
         * @param dst buffer where contents are written on
         * @param src_offset position where contents are read from
         * @param length contents length
         */
        abstract read(dst: ArrayBufferView, src_offset?: number, length?: number): Promise<void>;
        /**
         * for a range which will be written from CPU iteratively, make view to avoid copy (if backend allows)
         * if backend does not allow such operation, return newly allocated memory and send their contents to GPU when syncWriteViews is called
         * @param offset position where buffer-view begin from
         * @param length buffer-view length
         * @param number_type data format such as Float32, UInt8, and so on.
         */
        abstract getWriteView(offset: number, length: number, number_type: any): ArrayBufferView;
        /**
         * for a range which will be read from CPU iteratively, make view to avoid copy (if backend allows)
         * if backend does not allow such operation, return newly allocated memory and fill their contents from GPU when syncReadViews is called
         * @param offset position where buffer-view begin from
         * @param length buffer-view length
         * @param number_type data format such as Float32, UInt8, and so on.
         */
        abstract getReadView(offset: number, length: number, number_type: any): ArrayBufferView;
        /**
         * Sync buffered data into memory.
         */
        abstract syncWriteViews(): Promise<void>;
        /**
         * Sync memory data into buffer view.
         */
        abstract syncReadViews(): Promise<void>;
    }
}
declare namespace WebDNN {
    class BufferWebGPU extends Buffer {
        private static webgpuHandler;
        buffer: WebGPUBuffer;
        bufferView: Uint8Array;
        constructor(byteLength: number);
        write(src: ArrayBufferView, dst_offset?: number): Promise<void>;
        read<T extends ArrayBufferView>(dst: T, src_offset?: number, length?: number): Promise<void>;
        static init(webgpuHandler: WebGPUHandler): void;
        getWriteView(offset: number, length: number, number_type: any): ArrayBufferView;
        getReadView(offset: number, length: number, number_type: any): ArrayBufferView;
        syncWriteViews(): Promise<void>;
        syncReadViews(): Promise<void>;
    }
}
declare namespace WebDNN {
    class WebGPUHandler {
        static isBrowserSupported: boolean;
        private context;
        private commandQueue;
        private pipelineStates;
        init(): Promise<void>;
        createBuffer(arrayBuffer: ArrayBufferView): WebGPUBuffer;
        loadKernel(librarySource: string, namespace?: string): void;
        createCommandBuffer(): WebGPUCommandBuffer;
        getPipelineStateByName(name: string): WebGPUComputePipelineState;
        executeSinglePipelineState(name: string, threadgroupsPerGrid: WebGPUSize, threadsPerThreadgroup: WebGPUSize, buffers: (WebGPUBuffer | BufferWebGPU)[], getCompletedPromise?: boolean): Promise<void> | null;
        sync(): Promise<void>;
    }
}
interface WebGPURenderingContext {
    createCommandQueue(): WebGPUCommandQueue;
    createBuffer(data: ArrayBufferView): WebGPUBuffer;
    createLibrary(sourceCode: string): WebGPULibrary;
    createComputePipelineState(function_: WebGPUFunction): WebGPUComputePipelineState;
}
interface WebGPUFunction {
}
interface WebGPULibrary {
    functionNames: string[];
    functionWithName(name: string): WebGPUFunction;
}
interface WebGPUBuffer {
    contents: any;
}
interface WebGPUSize {
    width: number;
    height: number;
    depth: number;
}
interface WebGPUCommandQueue {
    createCommandBuffer(): WebGPUCommandBuffer;
}
interface WebGPUCommandBuffer {
    createComputeCommandEncoder(): WebGPUComputeCommandEncoder;
    commit(): void;
    completed: Promise<void>;
}
interface WebGPUCommandEncoder {
    endEncoding(): void;
}
interface WebGPUComputeCommandEncoder extends WebGPUCommandEncoder {
    setComputePipelineState(state: WebGPUComputePipelineState): void;
    setBuffer(buffer: WebGPUBuffer, offset: number, index: number): void;
    dispatch(threadgroupsPerGrid: WebGPUSize, threadsPerThreadgroup: WebGPUSize): void;
}
interface WebGPUComputePipelineState {
}
interface HTMLCanvasElement {
    getContext(contextId: "webgpu"): WebGPURenderingContext | null;
}
declare namespace WebDNN {
    interface WeightDecoder {
        decode(data: Uint8Array, memory_layout: MemoryLayout): Promise<Float32Array>;
    }
}
declare namespace WebDNN {
    class WeightDecoderRaw implements WeightDecoder {
        decode(data: Uint8Array, memory_layout: MemoryLayout): Promise<Float32Array>;
    }
}
declare var Zlib: any;
declare namespace WebDNN {
    class WeightDecoderEightbit implements WeightDecoder {
        static decode_table: number[];
        decode(data: Uint8Array, memory_layout: MemoryLayout): Promise<Float32Array>;
    }
}
declare namespace WebDNN {
    function get_weight_decoder(name: string): WeightDecoder;
}
declare namespace WebDNN {
    namespace util {
        /**
         *  Schedule function which is called too much frequently.
         */
        class DispatchScheduler {
            private scheduledCallbackId;
            private fn;
            /**
             * Register scheduled function. If already other function is scheduled, it is canceled and dispatcher will dispatch only
             * function which is registered at last.
             * @param fn scheduled function
             */
            request(fn: () => any): void;
            /**
             * Dispatch scheduled function just now. If no function is scheduled, dispatcher do nothing.
             */
            forceDispatch(): void;
            /**
             * Cancel scheduled function. If no function is scheduled, dispatcher do nothing.
             */
            cancel(): void;
        }
    }
}
declare let transformDelegate: (base: string) => string;
/**
 * Fetch delegate function.
 * Every fetch call in WebDNN is delegated to this function.
 * As default, `window.fetch` is set.
 * @type {(input:RequestInfo, init?:RequestInit)=>Promise<Response>}
 */
declare let fetchDelegate: (input: RequestInfo, init?: RequestInit) => Promise<Response>;
declare namespace WebDNN {
    /**
     * Register delegate function for transform url
     * @param url url which will be transformed
     */
    function transformUrl(url: string): string;
    /**
     * Register delegate function for transform url
     * @param delegate delegate function
     */
    function registerTransformDelegate(delegate: (base: string) => string): void;
    /**
     * Register delegate function for fetch
     * @param delegate delegate function
     */
    function registerFetchDelegate(delegate: (input: RequestInfo, init?: RequestInit) => Promise<Response>): void;
    /**
     * Fetch function. WebDNN API use this fetch function instead of original fetch function.
     * @param input Requested url
     * @param init Additional information about fetch
     * @returns Response
     */
    function fetch(input: RequestInfo, init?: RequestInit): Promise<Response>;
    /**
     * Read `Response.body` stream as ArrayBuffer. This function provide progress information by callback.
     * @param res Response object
     * @param callback Callback function.
     * @returns ArrayBuffer
     */
    function readArrayBufferProgressively(res: Response, callback?: (loaded: number, total: number) => any): Promise<ArrayBuffer>;
}
declare namespace WebDNN {
    interface GraphDescriptorWebGPU extends GraphDescriptor {
        memory_layout: MemoryLayout;
        kernel_source: string;
        exec_infos: GraphDescriptorWebGPUExecInfos[];
    }
    interface GraphDescriptorWebGPUExecInfos {
        entry_func_name: string;
        threadgroups_per_grid: WebGPUSize;
        threads_per_thread_group: WebGPUSize;
        meta_buffer: number[];
        unresolved_value_list: {
            offset: number;
            placeholder: Placeholder;
        }[];
    }
}
declare namespace WebDNN {
    class DescriptorRunnerWebGPU extends DescriptorRunner<GraphDescriptorWebGPU> {
        readonly backendName: string;
        webgpuHandler: WebGPUHandler;
        shaderLanguage: string;
        staticBuffer: BufferWebGPU | null;
        dynamicBuffer: BufferWebGPU | null;
        metaBuffers: BufferWebGPU[] | null;
        private inputViews;
        private outputViews;
        constructor(option?: any);
        init(): Promise<void>;
        private initializeBasicKernels();
        load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;
        initializeStaticBuffer(weightRawArray: ArrayBuffer): Promise<void>;
        initializeMetaBuffers(): Promise<void>;
        initializeDynamicBuffer(): Promise<void>;
        setDescriptor(descriptor: GraphDescriptorWebGPU): Promise<void>;
        compile(): Promise<void>;
        setPlaceholderValue(values: {
            [key: string]: number;
        }): Promise<void>;
        getInputViews(): Promise<SymbolicFloat32Array[]>;
        getOutputViews(): Promise<SymbolicFloat32Array[]>;
        run(): Promise<void>;
    }
}
declare namespace WebDNN {
    interface GraphDescriptorWebassembly extends GraphDescriptor {
        memory_layout: MemoryLayout;
    }
}
declare let WebAssembly: any;
declare namespace WebDNN {
    class DescriptorRunnerWebassembly extends DescriptorRunner<GraphDescriptorWebassembly> {
        readonly backendName: string;
        inputViews: Float32Array[] | null;
        outputViews: Float32Array[] | null;
        worker: Worker | null;
        worker_entry_js_path: any;
        worker_promise_reject_func: any;
        worker_initial_error: any;
        constructor(option?: any);
        init(): Promise<void>;
        load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;
        setPlaceholderValue(placeholders: {
            [p: string]: number;
        }): void;
        compile(): Promise<void>;
        loadWeights(weightsData: Uint8Array): Promise<void>;
        getInputViews(): Promise<SymbolicFloat32Array[]>;
        getOutputViews(): Promise<SymbolicFloat32Array[]>;
        run(): Promise<void>;
    }
}
declare namespace WebDNN {
    interface GraphDescriptorFallback extends GraphDescriptor {
        memory_layout: MemoryLayout;
        kernel_source: string;
        exec_infos: GraphDescriptorFallbackExecInfo[];
    }
    interface GraphDescriptorFallbackExecInfo {
        entry_func_name: string;
        inputs: string[];
        outputs: string[];
        weights: string[];
        call_option: any;
    }
}
declare namespace WebDNN {
    class DescriptorRunnerFallback extends DescriptorRunner<GraphDescriptorFallback> {
        readonly backendName: string;
        kernelObj: any;
        rawArray: Float32Array | null;
        variableArrays: Map<string, Float32Array> | null;
        inputViews: Float32Array[] | null;
        outputViews: Float32Array[] | null;
        init(): Promise<void>;
        load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;
        setPlaceholderValue(placeholders: {
            [p: string]: number;
        }): void;
        compile(): Promise<void>;
        private compileKernel();
        loadWeights(weightsData: Uint8Array): Promise<void>;
        run(): Promise<void>;
        wait_to_display(): Promise<{}>;
        getInputViews(): Promise<SymbolicFloat32Array[]>;
        getOutputViews(): Promise<SymbolicFloat32Array[]>;
    }
}
declare namespace WebDNN {
    const backends: {
        'webgpu': typeof DescriptorRunnerWebGPU;
        'webassembly': typeof DescriptorRunnerWebassembly;
        'fallback': typeof DescriptorRunnerFallback;
    };
    let runner: DescriptorRunner<GraphDescriptor> | null;
    let backendName: string;
    let DEBUG: boolean;
    function init(backendOrder?: string | string[], backendOptions?: {
        [key: string]: any;
    }): Promise<string>;
    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param backendOrder The trying order of backend names to be initialized.
     * @param backendOptions Backend options.
     * @param progressCallback callback which is called to notice the loading is progressing.
     */
    interface InitOption {
        backendOrder?: string | string[];
        backendOptions?: {
            [key: string]: any;
        };
        progressCallback?: (loaded: number, total: number) => any;
    }
    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param directory URL of directory that contains graph descriptor files (e.g. graph_fallback.json)
     * @param initOption Initialize option
     * @return Interface to input/output data and run the model.
     */
    function prepareAll(directory: string, initOption?: InitOption): Promise<GraphInterface>;
    /**
     * Interface to input/output data and run the model.
     */
    interface GraphInterface {
        /**
         * The name of backend.
         */
        backendName: string;
        /**
         * The buffers to write input data.
         */
        inputViews: SymbolicFloat32Array[];
        /**
         * The buffers to read output data.
         */
        outputViews: SymbolicFloat32Array[];
        /**
         * Run the model.
         */
        run: () => Promise<void>;
    }
}
declare namespace WebDNN {
    namespace Math {
        /**
         * Return indices of the top-K largest samples.
         * @param arr array
         * @param k number of indices
         * @returns {number[]} indices of top-K largest samples
         */
        function argmax(arr: number[], k?: number): number[];
        /**
         * Return indices of the top-K smallest samples.
         * @param arr array
         * @param k number of indices
         * @returns {number[]} indices of top-K smallest samples
         */
        function argmin(arr: number[], k?: number): number[];
    }
}
declare namespace WebDNN {
    /**
     * Check backend availability
     * @returns List of backend availability and default selected backend order
     */
    function getBackendAvailability(): {
        status: {
            [name: string]: boolean;
        };
        defaultOrder: string[];
    };
}
