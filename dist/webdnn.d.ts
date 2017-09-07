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
declare module 'webdnn/placeholder' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	/**
	 * @protected
	 */
	export interface Placeholder {
	    eval: string;
	}
	/**
	 * PlaceholderContext manages the placeholders
	 * @protected
	 */
	export default class PlaceholderContext {
	    private values;
	    constructor(values?: {
	        [key: string]: number | null;
	    });
	    readonly isResolved: boolean;
	    update(values: {
	        [key: string]: number | null;
	    }): void;
	    resolve(placeholder: any): any;
	    toString(): string;
	}

}
declare module 'webdnn/graph_descriptor/memory_layout' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { Placeholder } from 'webdnn/placeholder';
	/**
	 * @protected
	 */
	export interface Allocation {
	    name: string;
	    offset: number | Placeholder;
	    size: number | Placeholder;
	}
	/**
	 * @protected
	 */
	export interface ResolvedAllocation extends Allocation {
	    offset: number;
	    size: number;
	}
	/**
	 * @protected
	 */
	export interface MemoryLayout {
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
declare module 'webdnn/graph_descriptor/graph_descriptor' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { MemoryLayout } from 'webdnn/graph_descriptor/memory_layout';
	/**
	 * Graph Descriptor
	 * @protected
	 */
	export interface GraphDescriptor {
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
declare module 'webdnn/symbolic_typed_array/symbolic_typed_array' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { Allocation } from 'webdnn/graph_descriptor/memory_layout';
	import PlaceholderContext from 'webdnn/placeholder';
	/**
	 * SymbolicTypedArray is wrapper class of buffers used in DNN model.
	 */
	export abstract class SymbolicTypedArray<T extends Float32Array | Int32Array> {
	    protected ignoreOffsetOnActual: boolean;
	    protected arrayBuffer?: ArrayBuffer;
	    protected allocation: Allocation;
	    protected placeholderContext?: PlaceholderContext;
	    /**
	     * Convert symbolic buffer view into actual buffer view.
	     *
	     * @returns actual typed array
	     */
	    abstract toActual(): T;
	    /**
	     * toActual:
	     *
	     * If this buffer view is initialized based on placeholder offset or size and the placeholder is not resolved,
	     * the error is thrown.
	     */
	    /**
	     * @param {Allocation} allocation
	     * @param {PlaceholderContext} placeholderContext
	     * @param {boolean} ignoreOffsetOnActual
	     * @protected
	     */
	    constructor(allocation: Allocation, placeholderContext?: PlaceholderContext, ignoreOffsetOnActual?: boolean);
	    /**
	     * @protected
	     */
	    setArrayBuffer(arrayBuffer: any): void;
	    /**
	     * @protected
	     */
	    readonly name: string;
	    /**
	     * @protected
	     */
	    readonly isDynamic: boolean;
	    /**
	     * @protected
	     */
	    readonly offset: any;
	    /**
	     * The number of elements in this buffer. Actual byte size is `(length * SIZE_OF_FLOAT)`.
	     */
	    readonly length: number;
	    /**
	     * Sets a value or an array of values.
	     *
	     * @param array A typed or untyped array of values to set.
	     * @param offset The index at which the values will be written.
	     */
	    set(array: ArrayLike<number>, offset?: number): void;
	}

}
declare module 'webdnn/symbolic_typed_array/symbolic_float32array' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { SymbolicTypedArray } from 'webdnn/symbolic_typed_array/symbolic_typed_array';
	/**
	 * @protected
	 */
	export default class SymbolicFloat32Array extends SymbolicTypedArray<Float32Array> {
	    toActual(): Float32Array;
	}

}
declare module 'webdnn/descriptor_runner/descriptor_runner' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { GraphDescriptor } from 'webdnn/graph_descriptor/graph_descriptor';
	import PlaceholderContext from 'webdnn/placeholder';
	import SymbolicFloat32Array from 'webdnn/symbolic_typed_array/symbolic_float32array';
	import { BackendName } from 'webdnn/webdnn';
	/**
	 * @protected
	 */
	export interface DescriptorRunnerConstructor<D extends GraphDescriptor> {
	    new (option?: any): DescriptorRunner<D>;
	    checkAvailability(): boolean;
	}
	/**
	 * `DescriptorRunner` provides interface to execute DNN model and access input and output buffers.
	 */
	export abstract class DescriptorRunner<D extends GraphDescriptor> {
	    /**
	     * For Developper:
	     *
	     * `DescriptorRunner` executes computation based on `GraphDescriptor`.
	     *
	     * Typically, DescriptorRunner takes 3 steps to execute DNN model.
	     *
	     * 1. Initialize static configurations
	     *
	     *    Initialize things independent from runtime configuration.
	     *
	     *      - `init()`
	     *      - `load()`
	     *
	     * 2. Initialize dynamic configurations
	     *
	     *    Initialize things depend on runtime configuration such as batch size, input image size, etc.
	     *
	     *      - `setPlaceholderValue()`
	     *      - `getInputViews()`
	     *      - `getOutputViews()`
	     *
	     * 3. Execute the model
	     *
	     *      - `run()`
	     *
	     * You need to do step 1 and 2 only once. We recommend to call `WebDNN.prepareAll()` instead
	     * to call `GraphDescriptor#load()` directly. In that method, all procedures in step 1 and 2 are performed.
	     */
	    /**
	     * The name of active backend
	     */
	    readonly backendName: BackendName;
	    protected _running: boolean;
	    protected descriptor: D | null;
	    protected placeholderContext: PlaceholderContext | null;
	    /**
	     * @protected
	     */
	    ignoreCache: boolean;
	    /**
	     * Initialize this runner
	     *
	     * @protected
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
	     * @protected
	     */
	    abstract load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;
	    /**
	     * Set actual value into placeholders. If no placeholder is exist in graph descriptor, it's no need to call this function.
	     *
	     * @param values dictionary object of placeholder name and value pair
	     * @protected
	     */
	    abstract setPlaceholderValue(values: {
	        [key: string]: number;
	    }): Promise<void>;
	    /**
	     * Get input [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]] object
	     *
	     * @returns array of input [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]]
	     */
	    abstract getInputViews(): SymbolicFloat32Array[];
	    /**
	     * Get output [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]] object
	     *
	     * @returns array of output [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]]
	     */
	    abstract getOutputViews(): SymbolicFloat32Array[];
	    /**
	     * Run descriptor. You must call [[webdnn.DescriptorRunner.getInputViews|`getInputViews`]] and
	     * [[webdnn.DescriptorRunner.getOutputViews|`getOutputViews`]] before calling this function.
	     */
	    abstract run(): Promise<void>;
	    /**
	     * Return `true` if model is running.
	     * While running, calling run() again or modifying input is invalid.
	     */
	    readonly running: boolean;
	}

}
declare module 'webdnn/decoder/weight_decoder' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	/**
	 * @protected
	 */
	interface WeightDecoder {
	    decode(data: Uint8Array): Promise<Float32Array>;
	}
	export default WeightDecoder;

}
declare module 'webdnn/decoder/weight_decoder_eightbit' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import WeightDecoder from 'webdnn/decoder/weight_decoder';
	/**
	 * @protected
	 */
	export default class WeightDecoderEightbit implements WeightDecoder {
	    static decode_table: number[];
	    decode(data: Uint8Array): Promise<Float32Array>;
	}

}
declare module 'webdnn/decoder/weight_decoder_raw' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import WeightDecoder from 'webdnn/decoder/weight_decoder';
	/**
	 * @protected
	 */
	export default class WeightDecoderRaw implements WeightDecoder {
	    decode(data: Uint8Array): Promise<Float32Array>;
	}

}
declare module 'webdnn/decoder/get_weight_decoder' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import WeightDecoder from 'webdnn/decoder/weight_decoder';
	/**
	 * @protected
	 */
	export default function get_weight_decoder(name: string): WeightDecoder;

}
declare module 'webdnn/util/dispatch_scheduler' {
	/**
	 * Schedule function which is called too much frequently.
	 *
	 * @private
	 */
	export default class DispatchScheduler {
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
declare module 'webdnn/fetch' {
	/**
	 * @protected
	 */
	export interface WebDNNRequestInit extends RequestInit {
	    ignoreCache: boolean;
	    progressCallback?: (loaded: number, total: number) => any;
	}
	/**
	 * Transform url generated based on current active backend
	 * @param url transformed url
	 * @protected
	 */
	export function transformUrl(url: string): string;
	/**
	 * Register delegate function for transform url.
	 * @param delegate Delegate function which will be called with original url, and must return converted url strings.
	 * @protected
	 */
	export function registerTransformUrlDelegate(delegate: (base: string) => string): void;
	/**
	 * Fetch function. WebDNN API use this function instead of original `fetch` function.
	 * FIXME
	 * @param input Requested url
	 * @param init Additional information about webdnnFetch
	 * @param init.ignoreCache If true, cache is ignored by appending '?t=(timestamp)' to the end of request url.
	 * @returns Response
	 * @protected
	 */
	export default function webdnnFetch(input: RequestInfo, init?: WebDNNRequestInit): Promise<any>;
	/**
	 * Read `Response.body` stream as ArrayBuffer. This function provide progress information by callback.
	 * @param res Response object
	 * @param callback Callback function.
	 * @returns ArrayBuffer
	 * @protected
	 */
	export function readArrayBufferProgressively(res: Response, callback?: (loaded: number, total: number) => any): Promise<ArrayBuffer>;

}
declare module 'webdnn/graph_descriptor/graph_descriptor_fallback' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { GraphDescriptor } from 'webdnn/graph_descriptor/graph_descriptor';
	/**
	 * @protected
	 */
	export interface GraphDescriptorFallback extends GraphDescriptor {
	    kernel_source: string;
	    exec_infos: GraphDescriptorFallbackExecInfo[];
	}
	/**
	 * @protected
	 */
	export interface GraphDescriptorFallbackExecInfo {
	    entry_func_name: string;
	    inputs: string[];
	    outputs: string[];
	    weights: string[];
	    call_option: any;
	}

}
declare module 'webdnn/descriptor_runner/descriptor_runner_fallback' {
	import { GraphDescriptorFallback } from 'webdnn/graph_descriptor/graph_descriptor_fallback';
	import SymbolicFloat32Array from 'webdnn/symbolic_typed_array/symbolic_float32array';
	import { BackendName } from 'webdnn/webdnn';
	import { DescriptorRunner } from 'webdnn/descriptor_runner/descriptor_runner';
	/**
	 * @protected
	 */
	export default class DescriptorRunnerFallback extends DescriptorRunner<GraphDescriptorFallback> {
	    readonly backendName: BackendName;
	    private kernelObj;
	    private variableMap;
	    private inputViews;
	    private outputViews;
	    private staticBuffer;
	    private dynamicBuffer;
	    static checkAvailability(): boolean;
	    init(): Promise<void>;
	    load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;
	    private setDescriptor(descriptor);
	    private compile();
	    private initializeStaticBuffer(weightRawArray);
	    private initializeDynamicBuffer();
	    setPlaceholderValue(values: {
	        [key: string]: number;
	    }): Promise<void>;
	    run(): Promise<void>;
	    getInputViews(): SymbolicFloat32Array[];
	    getOutputViews(): SymbolicFloat32Array[];
	}

}
declare module 'webdnn/graph_descriptor/graph_descriptor_webassembly' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { Placeholder } from 'webdnn/placeholder';
	import { GraphDescriptor } from 'webdnn/graph_descriptor/graph_descriptor';
	/**
	 * @protected
	 */
	export interface GraphDescriptorWebassembly extends GraphDescriptor {
	    unresolved_value_lists: {
	        offset: number;
	        placeholder: Placeholder;
	    }[][];
	}

}
declare module 'webdnn/descriptor_runner/descriptor_runner_webassembly' {
	import { GraphDescriptorWebassembly } from 'webdnn/graph_descriptor/graph_descriptor_webassembly';
	import SymbolicFloat32Array from 'webdnn/symbolic_typed_array/symbolic_float32array';
	import { BackendName } from 'webdnn/webdnn';
	import { DescriptorRunner } from 'webdnn/descriptor_runner/descriptor_runner';
	/**
	 * @protected
	 */
	export default class DescriptorRunnerWebassembly extends DescriptorRunner<GraphDescriptorWebassembly> {
	    readonly backendName: BackendName;
	    private inputViews;
	    private outputViews;
	    private worker;
	    private worker_entry_js_path;
	    private worker_promise_reject_func;
	    private worker_initial_error;
	    static checkAvailability(): boolean;
	    constructor();
	    init(): Promise<void>;
	    load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;
	    setPlaceholderValue(values: {
	        [key: string]: number;
	    }): Promise<void>;
	    private setPlaceholderValueWorker(dynamicBufferSize, metaBufferFillArray);
	    private compile();
	    private loadWeights(weightsData);
	    getInputViews(): SymbolicFloat32Array[];
	    getOutputViews(): SymbolicFloat32Array[];
	    run(): Promise<void>;
	}

}
declare module 'webdnn/graph_descriptor/graph_descriptor_webgl' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { GraphDescriptor } from 'webdnn/graph_descriptor/graph_descriptor';
	/**
	 * @protecte
	 */
	export type ChannelMode = 'RGBA' | 'R';
	/**
	 * @protected
	 */
	export interface GraphDescriptorWebGL extends GraphDescriptor {
	    shader_sources: {
	        [name: string]: string;
	    };
	    exec_infos: GraphDescriptorWebGLExecInfos[];
	    variables: {
	        [variable_name: string]: {
	            variable_size: number;
	            allocation_name: string;
	        };
	    };
	    allocations: {
	        [allocation_name: string]: {
	            allocation_size: number;
	            channel_mode: ChannelMode;
	        };
	    };
	    constants_map: {
	        [variable_name: string]: {
	            size: number;
	            byte_offset: number;
	        };
	    };
	}
	/**
	 * @protected
	 */
	export interface GraphDescriptorWebGLExecInfos {
	    shader_name: string;
	    uniforms: {
	        [name: string]: {
	            type: 'int' | 'float' | 'vec2' | 'vec4' | 'sampler2D';
	            value: number;
	        };
	    };
	    inputs: [{
	        variable_name: string;
	        uniform_name: string;
	        value: number;
	    }];
	    output: string;
	    width: number;
	}

}
declare module 'webdnn/buffer/buffer' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	/**
	 * Abstract buffer interface. Read/write transactions are regarded as asynchronous operation.
	 *
	 * @protected
	 */
	export abstract class Buffer {
	    /**
	     * @property {number}
	     */
	    byteLength: number;
	    backend: string;
	    constructor(byteLength: number, backend: string);
	    /**
	     * Write contents onto specified position synchronously.
	     *
	     * @param {ArrayBufferView} src contents source buffer
	     * @param {number} offset position where contents are written on
	     */
	    abstract write(src: ArrayBufferView, offset?: number): Promise<void>;
	    /**
	     * Read contents from specified position synchronously.
	     *
	     * @param {Float32ArrayConstructor | Int32ArrayConstructor} dst buffer where contents are written on
	     * @param {number} offset position where contents are read from
	     * @param {length} length contents length
	     */
	    abstract read(dst: Float32ArrayConstructor | Int32ArrayConstructor, offset?: number, length?: number): Promise<void>;
	    /**
	     * for a range which will be written from CPU iteratively, make view to avoid copy (if backend allows)
	     * if backend does not allow such operation, return newly allocated memory and send their contents to GPU when syncWriteViews is called
	     *
	     * @param {number} offset position where buffer-view begin from
	     * @param {number} length buffer-view length
	     * @param {Int32ArrayConstructor|Float32ArrayConstructor} type data format such as Float32Array, Int32Array, and so on.
	     */
	    abstract getWriteView(offset?: number, length?: number, type?: Int32ArrayConstructor): Int32Array;
	    abstract getWriteView(offset?: number, length?: number, type?: Float32ArrayConstructor): Float32Array;
	    /**
	     * for a range which will be read from CPU iteratively, make view to avoid copy (if backend allows)
	     * if backend does not allow such operation, return newly allocated memory and fill their contents from GPU when syncReadViews is called
	     *
	     * @param {number} offset position where buffer-view begin from
	     * @param {number} length buffer-view length
	     * @param {Int32ArrayConstructor|Float32ArrayConstructor} type data format such as Float32Array, Int32Array, and so on.
	     */
	    abstract getReadView(offset?: number, length?: number, type?: Int32ArrayConstructor): Int32Array;
	    abstract getReadView(offset?: number, length?: number, type?: Float32ArrayConstructor): Float32Array;
	    /**
	     * Sync buffered data into memory.
	     *
	     * @see Buffer#getWriteView
	     */
	    abstract syncWriteViews(): Promise<void>;
	    /**
	     * Sync memory data into buffer view.
	     *
	     * @see Buffer#getReadView
	     */
	    abstract syncReadViews(): Promise<void>;
	}

}
declare module 'webdnn' {
	}
