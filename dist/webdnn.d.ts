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
	     * Unix timestamp when this graph descriptor is generated
	     */
	    converted_at: number;
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
	import PlaceholderContext, { Placeholder } from 'webdnn/placeholder';
	/**
	 * @protected
	 */
	export abstract class SymbolicTypedArray<T extends Float32Array | Int32Array> {
	    protected placeholderContext: PlaceholderContext | null;
	    /**
	     * @protected
	     */
	    readonly _length: number | Placeholder;
	    /**
	     * @protected
	     */
	    readonly _byteOffset: number | Placeholder;
	    /**
	     * The size in bytes of each element in the array.
	     */
	    readonly BYTES_PER_ELEMENT: number;
	    /**
	     * @protected
	     */
	    protected _buffer: ArrayBufferLike | null;
	    /**
	     * @protected
	     */
	    name: string;
	    /**
	     * @protected
	     */
	    constructor(buffer?: ArrayBufferLike | null, byteOffset?: number | Placeholder, length?: number | Placeholder, placeholderContext?: PlaceholderContext | null);
	    /**
	     * Convert SymbolicTypedArray instance into actual TypedArray instance.
	     *
	     * @returns actual typed array
	     */
	    abstract toActual(): T;
	    /**
	     * The ArrayBuffer instance referenced by the array.
	     */
	    /**
	     * The ArrayBuffer instance referenced by the array.
	     */
	    buffer: ArrayBufferLike;
	    /**
	     * The length in bytes of the array.
	     */
	    readonly byteLength: number;
	    /**
	     * The number in this buffer. Actual offset size is `(offset * SIZE_OF_FLOAT)`.
	     */
	    readonly offset: number;
	    /**
	     * @protected
	     */
	    readonly isDynamic: boolean;
	    /**
	     * The number of elements in this buffer. Actual byte size is `(length * SIZE_OF_FLOAT)`.
	     */
	    readonly length: number;
	    /**
	     * The offset in bytes of the array.
	     */
	    readonly byteOffset: any;
	    /**
	     * Returns the this object after copying a section of the array identified by start and end
	     * to the same array starting at position target
	     * @param target If target is negative, it is treated as length+target where length is the
	     * length of the array.
	     * @param start If start is negative, it is treated as length+start. If end is negative, it
	     * is treated as length+end.
	     * @param end If not specified, length of the this object is used as its default value.
	     */
	    copyWithin(target: number, start: number, end?: number): this;
	    /**
	     * Returns the this object after filling the section identified by start and end with value
	     * @param value value to fill array section with
	     * @param start index to start filling the array at. If start is negative, it is treated as
	     * length+start where length is the length of the array.
	     * @param end index to stop filling the array at. If end is negative, it is treated as
	     * length+end.
	     */
	    fill(value: number, start?: number, end?: number): this;
	    /**
	     * Returns the index of the first occurrence of a value in an array.
	     * @param searchElement The value to locate in the array.
	     * @param fromIndex The array index at which to begin the search. If fromIndex is omitted, the
	     *  search starts at index 0.
	     */
	    indexOf(searchElement: number, fromIndex?: number): number;
	    /**
	     * Adds all the elements of an array separated by the specified separator string.
	     * @param separator A string used to separate one element of an array from the next in the
	     * resulting String. If omitted, the array elements are separated with a comma.
	     */
	    join(separator?: string): string;
	    /**
	     * Returns the index of the last occurrence of a value in an array.
	     * @param searchElement The value to locate in the array.
	     * @param fromIndex The array index at which to begin the search. If fromIndex is omitted, the
	     * search starts at index 0.
	     */
	    lastIndexOf(searchElement: number, fromIndex?: number): number;
	    /**
	     * Sorts an array.
	     * @param compareFn The name of the function used to determine the order of the elements. If
	     * omitted, the elements are sorted in ascending, ASCII character order.
	     */
	    sort(compareFn?: (a: number, b: number) => number): this;
	    includes(searchElement: number, fromIndex?: number | undefined): boolean;
	    /**
	     * Sets a value or an array of values.
	     * @param array A typed or untyped array of values to set.
	     * @param offset The index in the current array at which the values are to be written.
	     */
	    set(array: ArrayLike<number>, offset?: number | undefined): void;
	    /**
	     * Converts a number to a string by using the current locale.
	     */
	    toLocaleString(): string;
	    /**
	     * Returns a string representation of an array.
	     */
	    toString(): string;
	    /** @protected */
	    [Symbol.iterator](): IterableIterator<number>;
	    /**
	     * Returns an iterable of key, value pairs for every entry in the array
	     */
	    entries(): IterableIterator<[number, number]>;
	    /**
	     * Returns an iterable of keys in the array
	     */
	    keys(): IterableIterator<number>;
	    /**
	     * Returns an iterable of values in the array
	     */
	    values(): IterableIterator<number>;
	}

}
declare module 'webdnn/symbolic_typed_array/symbolic_float32array' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { SymbolicTypedArray } from 'webdnn/symbolic_typed_array/symbolic_typed_array';
	/**
	 * Typed array used for input and output variables of [[webdnn.DescriptorRunner| `DescriptorRunner`]].
	 * You can use `SymbolicFloat32Array` almost as same as `Float32Array`.
	 *
	 * To convert `SymbolicFloat32Array` into actual `Float32Array`, use [[webdnn.SymbolicFloat32Array.toActual| `toActual()`]]
	 *
	 * ```js
	 *
	 * let result = runner.outputs[0];  //runner.outputs is array of SymbolicFloat32Array
	 *
	 * // SymbolicFloat32Array does NOT support index access
	 * console.log(result[0]);
	 * >>> undefined
	 *
	 * // By conversion, you can access each element by index
	 * console.log(result.toActual()[0]);
	 * >>> 1.00  // Actual result
	 * ```
	 */
	export default class SymbolicFloat32Array extends SymbolicTypedArray<Float32Array> implements Float32Array {
	    /** @protected */
	    [Symbol.toStringTag]: "Float32Array";
	    /** @protected */
	    [index: number]: number;
	    /**
	     * The size in bytes of each element in SymbolicFloat32Array.
	     */
	    static readonly BYTES_PER_ELEMENT: number;
	    /**
	     * The size in bytes of each element in the array.
	     */
	    readonly BYTES_PER_ELEMENT: number;
	    /**
	     * Convert SymbolicTypedArray instance into actual TypedArray instance.
	     *
	     * @returns actual typed array
	     */
	    toActual(): Float32Array;
	    /**
	     * Determines whether all the members of an array satisfy the specified test.
	     * @param callbackfn A function that accepts up to three arguments. The every method calls
	     * the callbackfn function for each element in array1 until the callbackfn returns false,
	     * or until the end of the array.
	     * @param thisArg An object to which the this keyword can refer in the callbackfn function.
	     * If thisArg is omitted, undefined is used as the this value.
	     */
	    every(callbackfn: (value: number, index: number, array: Float32Array) => boolean, thisArg?: any): boolean;
	    /**
	     * Returns the elements of an array that meet the condition specified in a callback function.
	     * @param callbackfn A function that accepts up to three arguments. The filter method calls
	     * the callbackfn function one time for each element in the array.
	     * @param thisArg An object to which the this keyword can refer in the callbackfn function.
	     * If thisArg is omitted, undefined is used as the this value.
	     */
	    filter(callbackfn: (value: number, index: number, array: Float32Array) => any, thisArg?: any): Float32Array;
	    /**
	     * Returns the value of the first element in the array where predicate is true, and undefined
	     * otherwise.
	     * @param predicate find calls predicate once for each element of the array, in ascending
	     * order, until it finds one where predicate returns true. If such an element is found, find
	     * immediately returns that element value. Otherwise, find returns undefined.
	     * @param thisArg If provided, it will be used as the this value for each invocation of
	     * predicate. If it is not provided, undefined is used instead.
	     */
	    find(predicate: (value: number, index: number, obj: Float32Array) => boolean, thisArg?: any): number | undefined;
	    /**
	     * Returns the index of the first element in the array where predicate is true, and -1
	     * otherwise.
	     * @param predicate find calls predicate once for each element of the array, in ascending
	     * order, until it finds one where predicate returns true. If such an element is found,
	     * findIndex immediately returns that element index. Otherwise, findIndex returns -1.
	     * @param thisArg If provided, it will be used as the this value for each invocation of
	     * predicate. If it is not provided, undefined is used instead.
	     */
	    findIndex(predicate: (value: number, index: number, obj: Float32Array) => boolean, thisArg?: any): number;
	    /**
	     * Performs the specified action for each element in an array.
	     * @param callbackfn  A function that accepts up to three arguments. forEach calls the
	     * callbackfn function one time for each element in the array.
	     * @param thisArg  An object to which the this keyword can refer in the callbackfn function.
	     * If thisArg is omitted, undefined is used as the this value.
	     */
	    forEach(callbackfn: (value: number, index: number, array: Float32Array) => void, thisArg?: any): void;
	    /**
	     * Calls a defined callback function on each element of an array, and returns an array that
	     * contains the results.
	     * @param callbackfn A function that accepts up to three arguments. The map method calls the
	     * callbackfn function one time for each element in the array.
	     * @param thisArg An object to which the this keyword can refer in the callbackfn function.
	     * If thisArg is omitted, undefined is used as the this value.
	     */
	    map(callbackfn: (value: number, index: number, array: Float32Array) => number, thisArg?: any): Float32Array;
	    /**
	     * Calls the specified callback function for all the elements in an array. The return value of
	     * the callback function is the accumulated result, and is provided as an argument in the next
	     * call to the callback function.
	     * @param callbackfn A function that accepts up to four arguments. The reduce method calls the
	     * callbackfn function one time for each element in the array.
	     * @param initialValue If initialValue is specified, it is used as the initial value to start
	     * the accumulation. The first call to the callbackfn function provides this value as an argument
	     * instead of an array value.
	     */
	    reduce(callbackfn: (previousValue: number, currentValue: number, currentIndex: number, array: Float32Array) => number): number;
	    reduce(callbackfn: (previousValue: number, currentValue: number, currentIndex: number, array: Float32Array) => number, initialValue: number): number;
	    /**
	     * Calls the specified callback function for all the elements in an array. The return value of
	     * the callback function is the accumulated result, and is provided as an argument in the next
	     * call to the callback function.
	     * @param callbackfn A function that accepts up to four arguments. The reduce method calls the
	     * callbackfn function one time for each element in the array.
	     * @param initialValue If initialValue is specified, it is used as the initial value to start
	     * the accumulation. The first call to the callbackfn function provides this value as an argument
	     * instead of an array value.
	     */
	    reduce<U>(callbackfn: (previousValue: U, currentValue: number, currentIndex: number, array: Float32Array) => U, initialValue: U): U;
	    /**
	     * Calls the specified callback function for all the elements in an array, in descending order.
	     * The return value of the callback function is the accumulated result, and is provided as an
	     * argument in the next call to the callback function.
	     * @param callbackfn A function that accepts up to four arguments. The reduceRight method calls
	     * the callbackfn function one time for each element in the array.
	     * @param initialValue If initialValue is specified, it is used as the initial value to start
	     * the accumulation. The first call to the callbackfn function provides this value as an
	     * argument instead of an array value.
	     */
	    reduceRight(callbackfn: (previousValue: number, currentValue: number, currentIndex: number, array: Float32Array) => number): number;
	    reduceRight(callbackfn: (previousValue: number, currentValue: number, currentIndex: number, array: Float32Array) => number, initialValue: number): number;
	    /**
	     * Calls the specified callback function for all the elements in an array, in descending order.
	     * The return value of the callback function is the accumulated result, and is provided as an
	     * argument in the next call to the callback function.
	     * @param callbackfn A function that accepts up to four arguments. The reduceRight method calls
	     * the callbackfn function one time for each element in the array.
	     * @param initialValue If initialValue is specified, it is used as the initial value to start
	     * the accumulation. The first call to the callbackfn function provides this value as an argument
	     * instead of an array value.
	     */
	    reduceRight<U>(callbackfn: (previousValue: U, currentValue: number, currentIndex: number, array: Float32Array) => U, initialValue: U): U;
	    /**
	     * Reverses the elements in an Array.
	     */
	    reverse(): Float32Array;
	    /**
	     * Returns a section of an array.
	     * @param start The beginning of the specified portion of the array.
	     * @param end The end of the specified portion of the array.
	     */
	    slice(start?: number, end?: number): Float32Array;
	    /**
	     * Determines whether the specified callback function returns true for any element of an array.
	     * @param callbackfn A function that accepts up to three arguments. The some method calls the
	     * callbackfn function for each element in array1 until the callbackfn returns true, or until
	     * the end of the array.
	     * @param thisArg An object to which the this keyword can refer in the callbackfn function.
	     * If thisArg is omitted, undefined is used as the this value.
	     */
	    some(callbackfn: (value: number, index: number, array: Float32Array) => boolean, thisArg?: any): boolean;
	    /**
	     * Gets a new Float32Array view of the ArrayBuffer store for this array, referencing the elements
	     * at begin, inclusive, up to end, exclusive.
	     * @param begin The index of the beginning of the array.
	     * @param end The index of the end of the array.
	     */
	    subarray(begin: number, end?: number): Float32Array;
	    /** @protected */
	    includes(searchElement: number, fromIndex?: number | undefined): boolean;
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
	export interface DescriptorRunnerOptions {
	    transformUrlDelegate?: (base: string) => string;
	}
	/**
	 * @protected
	 */
	export interface DescriptorRunnerConstructor<D extends GraphDescriptor, P> {
	    new (option: DescriptorRunnerOptions): DescriptorRunner<D, P>;
	    checkAvailability(): boolean;
	}
	/**
	 * `DescriptorRunner` provides interface to execute DNN model and access input and output buffers.
	 */
	export abstract class DescriptorRunner<D extends GraphDescriptor, P> {
	    constructor(option?: DescriptorRunnerOptions);
	    /**
	     * For Developer:
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
	     * The backend name
	     */
	    readonly backendName: BackendName;
	    readonly transformUrlDelegate: (base: string) => string;
	    /**
	     * The descriptor
	     */
	    protected descriptor: D | null;
	    /**
	     * placeholder context which manages all placeholders and their values
	     */
	    protected placeholderContext: PlaceholderContext | null;
	    /**
	     * input arrays
	     */
	    inputs: SymbolicFloat32Array[];
	    /**
	     * outputs arrays
	     */
	    outputs: SymbolicFloat32Array[];
	    /**
	     * Return `true` if this backend is available in this environment.
	     * @returns {boolean}
	     */
	    static checkAvailability(): boolean;
	    /**
	     * Initialize descriptor runner asynchronously
	     * @returns {Promise<void>} Promise object which is resolved when the initialization finished.
	     * @protected
	     */
	    abstract init(): Promise<void>;
	    /**
	     * set graph descriptor and parameters
	     * @protected
	     */
	    abstract setDescriptorAndParameters(descriptor: D, parameters: P): Promise<void>;
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
	    abstract fetchDescriptor(directory: string): Promise<D>;
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
	    abstract fetchParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<P>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    abstract restoreCachedDescriptor(directory: string): Promise<D | null>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    abstract restoreCachedParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<P | null>;
	    /**
	     * save cache
	     * @protected
	     */
	    abstract saveCache(directory: string, descriptor: D, parameters: P): Promise<void>;
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
	     * @protected
	     * @returns array of input [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]]
	     * @deprecated use [[webdnn.DescriptorRunner.inputs| `inputs`]] instead.
	     */
	    abstract getInputViews(): SymbolicFloat32Array[];
	    /**
	     * Get output [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]] object
	     *
	     * @protected
	     * @returns array of output [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]]
	     * @deprecated use [[webdnn.DescriptorRunner.outputs| `outputs`]] instead.
	     */
	    abstract getOutputViews(): SymbolicFloat32Array[];
	    /**
	     * Run descriptor. You must call [[webdnn.DescriptorRunner.getInputViews|`getInputViews`]] and
	     * [[webdnn.DescriptorRunner.getOutputViews|`getOutputViews`]] before calling this function.
	     */
	    abstract run(): Promise<void>;
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
	export default function getWeightDecoder(name: string): WeightDecoder;

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
	 * Fetch function. WebDNN API use this function instead of original `fetch` function.
	 * FIXME
	 * @param input Requested url
	 * @param transformUrlDelegate url transform function
	 * @param init? Additional information about webdnnFetch
	 * @param init?.ignoreCache If true, cache is ignored by appending '?t=(timestamp)' to the end of request url.
	 * @returns Response
	 * @protected
	 */
	export default function webdnnFetch(input: RequestInfo, transformUrlDelegate: (base: string) => string, init?: WebDNNRequestInit): Promise<any>;
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
	import { DescriptorRunner, DescriptorRunnerOptions } from 'webdnn/descriptor_runner/descriptor_runner';
	/**
	 * @protected
	 */
	export default class DescriptorRunnerFallback extends DescriptorRunner<GraphDescriptorFallback, ArrayBuffer> {
	    readonly backendName: BackendName;
	    private kernelObj;
	    private variableMap;
	    private staticBuffer;
	    private dynamicBuffer;
	    private directory;
	    static checkAvailability(): boolean;
	    constructor(options?: DescriptorRunnerOptions);
	    init(): Promise<void>;
	    setDescriptorAndParameters(descriptor: GraphDescriptorFallback, parameters: ArrayBuffer): Promise<void>;
	    fetchDescriptor(directory: string): Promise<any>;
	    fetchParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    restoreCachedDescriptor(directory: string): Promise<GraphDescriptorFallback | null>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    restoreCachedParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer | null>;
	    /**
	     * save cache
	     */
	    saveCache(directory: string, descriptor: GraphDescriptorFallback, parameters: ArrayBuffer): Promise<void>;
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
	import { DescriptorRunner, DescriptorRunnerOptions } from 'webdnn/descriptor_runner/descriptor_runner';
	/**
	 * @protected
	 */
	export default class DescriptorRunnerWebassembly extends DescriptorRunner<GraphDescriptorWebassembly, ArrayBuffer> {
	    readonly backendName: BackendName;
	    private worker;
	    private worker_entry_js_path;
	    private worker_promise_reject_func;
	    private worker_initial_error;
	    private directory;
	    static checkAvailability(): boolean;
	    constructor(options?: DescriptorRunnerOptions);
	    init(): Promise<void>;
	    private absolutePath(path);
	    setDescriptorAndParameters(descriptor: GraphDescriptorWebassembly, parameters: ArrayBuffer): Promise<void>;
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
	    fetchDescriptor(directory: string): Promise<GraphDescriptorWebassembly>;
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
	    fetchParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    restoreCachedDescriptor(directory: string): Promise<GraphDescriptorWebassembly | null>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    restoreCachedParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer | null>;
	    /**
	     * save cache
	     */
	    saveCache(directory: string, descriptor: GraphDescriptorWebassembly, parameters: ArrayBuffer): Promise<void>;
	    setPlaceholderValue(values: {
	        [key: string]: number;
	    }): Promise<void>;
	    private setPlaceholderValueWorker(dynamicBufferSize, metaBufferFillArray);
	    private compile(worker_src);
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
	import { Placeholder } from 'webdnn/placeholder';
	import { GraphDescriptor } from 'webdnn/graph_descriptor/graph_descriptor';
	import { Allocation, MemoryLayout, ResolvedAllocation } from 'webdnn/graph_descriptor/memory_layout';
	/**
	 * @protected
	 */
	export type ChannelMode = 'RGBA' | 'R';
	/**
	 * @protected
	 */
	export interface WebGLMemoryLayout extends MemoryLayout {
	    'static': {
	        size: -1;
	        allocations: {
	            [index: string]: ResolvedWebGLAllocation;
	        };
	    };
	    dynamic: {
	        size: -1;
	        allocations: {
	            [index: string]: WebGLAllocation;
	        };
	    };
	    mapping: {
	        [variableName: string]: string;
	    };
	}
	/**
	 * @protected
	 */
	export interface ResolvedWebGLAllocation extends ResolvedAllocation, WebGLAllocation {
	    name: string;
	    offset: -1;
	    size: number;
	    width: number;
	    height: number;
	    channel_mode: ChannelMode;
	}
	/**
	 * @protected
	 */
	export interface WebGLAllocation extends Allocation {
	    name: string;
	    offset: -1;
	    size: number | Placeholder;
	    width: number | Placeholder;
	    height: number | Placeholder;
	    channel_mode: ChannelMode;
	}
	/**
	 * @protected
	 */
	export interface GraphDescriptorWebGL extends GraphDescriptor {
	    shader_sources: {
	        [name: string]: string;
	    };
	    exec_infos: GraphDescriptorWebGLExecInfos[];
	    memory_layout: WebGLMemoryLayout;
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
	            type: 'int' | 'float' | 'vec2' | 'vec3' | 'vec4' | 'ivec2' | 'ivec3' | 'ivec4' | 'sampler2D';
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
declare namespace WebGL2RenderingContext {
}


declare class WebGL2RenderingContext extends WebGLRenderingContext {
    RED: GLenum;
    RGBA32F: GLenum;
    R32F: GLenum;
    SYNC_GPU_COMMANDS_COMPLETE: GLenum;
    ALREADY_SIGNALED: GLenum;
    CONDITION_SATISFIED: GLenum;

    createVertexArray(): WebGLVertexArrayObject;

    bindVertexArray(vertexArray: WebGLVertexArrayObject): void;

    fenceSync(condition: GLenum, flags: GLbitfield): WebGLSync;

    clientWaitSync(sync: WebGLSync, flags: GLbitfield, timeout: 0): GLenum;

    deleteSync(sync: WebGLSync): void;
}

declare class WebGLVertexArrayObject {

}

declare class WebGLSync {

}

declare interface WebGLVertexArrayObjectExtension {
    bindVertexArrayOES(vertexArray: WebGLVertexArrayObject): void;

    createVertexArrayOES(): WebGLVertexArrayObject;
}
declare module 'webdnn/webgl_handler' {
	/// <reference path="webgl2.d.ts" />
	/**
	 * @protected
	 */
	export function isWebGL2(gl: WebGLRenderingContext | WebGL2RenderingContext): gl is WebGL2RenderingContext;
	/**
	 * @protected
	 */
	export default class WebGLHandler {
	    static IS_SAFARI: boolean;
	    readonly gl: WebGLRenderingContext | WebGL2RenderingContext;
	    static getInstance(): WebGLHandler;
	    /**
	     * WebGLHandler is singleton class and instantiate directly is forbidden (constructor is hidden).
	     *
	     * Since the number of GPU contexts may be limited, the handler is used as a singleton
	     * and only one context is shared among multiple runners.
	     */
	    private constructor();
	    createTexture(textureWidth: number, textureHeight: number, internalFormat: number, format: number): WebGLTexture;
	    createVertexShader(source: string): WebGLShader;
	    createFragmentShader(source: string): WebGLShader;
	    createShader(type: number, source: string): WebGLShader;
	    createProgram(vertexShader: WebGLShader, fragmentShader: WebGLShader): WebGLProgram;
	    createArrayBuffer(vertexArray: number | Float32Array): WebGLBuffer;
	    createFrameBuffer(): WebGLFramebuffer;
	    bindArrayBuffer(buffer: WebGLBuffer): void;
	    bindFrameBuffer(frameBuffer: WebGLFramebuffer, width: number, height: number): void;
	    useProgram(program: WebGLProgram): void;
	    deleteTexture(texture: WebGLTexture): void;
	    static initializeWebGL2Context(canvas?: HTMLCanvasElement): WebGLRenderingContext | null;
	    static initializeWebGL1Context(canvas?: HTMLCanvasElement): WebGLRenderingContext | null;
	    static initializeContext(): WebGLRenderingContext | null;
	    /**
	     * Check whether WebGL is supported or not
	     * @protected
	     */
	    static checkAvailability(): boolean;
	    waitForComplete(): Promise<void>;
	    readonly MAX_TEXTURE_SIZE: number;
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
declare module 'webdnn/buffer/buffer_webgl' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { ChannelMode } from 'webdnn/graph_descriptor/graph_descriptor_webgl';
	import { Buffer } from 'webdnn/buffer/buffer';
	/**
	 * @protected
	 */
	export default class BufferWebGL extends Buffer {
	    private handler;
	    readonly channelMode: ChannelMode;
	    readonly elementsPerPixel: number;
	    readonly pixelStride: number;
	    readonly array: Float32Array;
	    readonly textureWidth: number;
	    readonly textureHeight: number;
	    readonly textureFormat: number;
	    readonly textureInternalFormat: number;
	    private _texture;
	    readonly name: string;
	    private readTextureUnitIndices;
	    private isBoundToDrawFrameBuffer;
	    constructor(byteLength: number, textureWidth: number, textureHeight: number, name: string, array: Float32Array | null, channelMode: ChannelMode);
	    readonly texture: WebGLTexture | null;
	    readonly length: number;
	    /**
	     * Write contents onto specified position synchronously.
	     *
	     * @param {ArrayBufferView} src contents source buffer
	     * @param {number} offset position where contents are written on
	     */
	    write(src: ArrayBufferView, offset?: number): Promise<void>;
	    /**
	     * Read contents from specified position synchronously.
	     *
	     * @param {Float32ArrayConstructor | Int32ArrayConstructor} dst buffer where contents are written on
	     * @param {number} offset position where contents are read from
	     * @param {length} length contents length
	     */
	    read(dst: Float32ArrayConstructor | Int32ArrayConstructor, offset?: number, length?: number): Promise<void>;
	    /**
	     * for a range which will be written from CPU iteratively, make view to avoid copy (if backend allows)
	     * if backend does not allow such operation, return newly allocated memory and send their contents to GPU when syncWriteViews is called
	     *
	     * @param {number} offset position where buffer-view begin from
	     * @param {number} length buffer-view length
	     * @param {Int32ArrayConstructor|Float32ArrayConstructor} type data format such as Float32Array, Int32Array, and so on.
	     */
	    getWriteView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
	    getWriteView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
	    /**
	     * for a range which will be read from CPU iteratively, make view to avoid copy (if backend allows)
	     * if backend does not allow such operation, return newly allocated memory and fill their contents from GPU when syncReadViews is called
	     *
	     * @param {number} offset position where buffer-view begin from
	     * @param {number} length buffer-view length
	     * @param {Int32ArrayConstructor|Float32ArrayConstructor} type data format such as Float32Array, Int32Array, and so on.
	     */
	    getReadView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
	    getReadView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
	    /**
	     * Sync buffered data into memory.
	     *
	     * @see Buffer#getWriteView
	     */
	    syncWriteViews(): Promise<void>;
	    /**
	     * Sync memory data into buffer view.
	     *
	     * @see Buffer#getReadView
	     */
	    syncReadViews(): Promise<void>;
	    bindToReadTexture(unit: number): Promise<void>;
	    unbindFromReadTexture(): void;
	    bindToDrawTexture(): void;
	    unbindFromDrawTexture(): void;
	    private pack(array);
	    private unpack(array);
	    private allocateTexture();
	}

}
declare module 'webdnn/descriptor_runner/descriptor_runner_webgl' {
	import { GraphDescriptorWebGL } from 'webdnn/graph_descriptor/graph_descriptor_webgl';
	import SymbolicFloat32Array from 'webdnn/symbolic_typed_array/symbolic_float32array';
	import { BackendName } from 'webdnn/webdnn';
	import { DescriptorRunner, DescriptorRunnerOptions } from 'webdnn/descriptor_runner/descriptor_runner';
	/**
	 * @protected
	 */
	export default class DescriptorRunnerWebGL extends DescriptorRunner<GraphDescriptorWebGL, ArrayBuffer> {
	    readonly backendName: BackendName;
	    private runtimeInfo;
	    private handler;
	    private vertexShader;
	    private programs;
	    private buffers;
	    static checkAvailability(): boolean;
	    constructor(options?: DescriptorRunnerOptions);
	    init(): Promise<void>;
	    fetchDescriptor(directory: string): Promise<any>;
	    fetchParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    restoreCachedDescriptor(directory: string): Promise<GraphDescriptorWebGL | null>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    restoreCachedParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer | null>;
	    /**
	     * save cache
	     */
	    saveCache(directory: string, descriptor: GraphDescriptorWebGL, parameters: ArrayBuffer): Promise<void>;
	    setDescriptorAndParameters(descriptor: GraphDescriptorWebGL, parameters: ArrayBuffer): Promise<void>;
	    private initializeStaticBuffer(weightRawArray);
	    private initializeDynamicBuffer();
	    private setDescriptor(descriptor);
	    private compile();
	    setPlaceholderValue(values: {
	        [key: string]: number;
	    }): Promise<void>;
	    getInputViews(): SymbolicFloat32Array[];
	    getOutputViews(): SymbolicFloat32Array[];
	    private buildPipeline();
	    run(): Promise<void>;
	}

}
declare module 'webdnn/webgpu_handler' {
	/// <reference path="webgpu.d.ts" />
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import BufferWebGPU from 'webdnn/buffer/buffer_webgpu';
	/**
	 * @protected
	 */
	export default class WebGPUHandler {
	    private context;
	    private commandQueue;
	    private pipelineStates;
	    private commandBuffer;
	    static getInstance(): WebGPUHandler;
	    /**
	     * WebGPUHandler is singleton class and instantiate directly is forbidden (constructor is hidden).
	     *
	     * Since the number of GPU contexts may be limited, the handler is used as a singleton
	     * and only one context is shared among multiple runners.
	     */
	    private constructor();
	    createBuffer(arrayBuffer: ArrayBufferView): WebGPUBuffer;
	    loadKernel(librarySource: string, namespace?: string): void;
	    createCommandBuffer(): WebGPUCommandBuffer;
	    getPipelineStateByName(name: string): WebGPUComputePipelineState;
	    executeSinglePipelineState(name: string, threadgroupsPerGrid: WebGPUSize, threadsPerThreadgroup: WebGPUSize, buffers: (WebGPUBuffer | BufferWebGPU)[], getCompletedPromise?: boolean): Promise<void> | null;
	    sync(): Promise<void>;
	}
	/**
	 * Flag whether WebGPU is supported or not
	 * @protected
	 */
	export const IS_WEBGPU_SUPPORTED: boolean;

}
declare module 'webdnn/buffer/buffer_webgpu' {
	import { Buffer } from 'webdnn/buffer/buffer';
	/**
	 * @protected
	 */
	export default class BufferWebGPU extends Buffer {
	    buffer: WebGPUBuffer;
	    bufferView: Uint8Array;
	    private handler;
	    constructor(byteLength: number);
	    write(src: ArrayBufferView, dst_offset?: number): Promise<void>;
	    read(dst: any, src_offset?: number, length?: number): Promise<void>;
	    getWriteView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
	    getWriteView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
	    getReadView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
	    getReadView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
	    syncWriteViews(): Promise<void>;
	    syncReadViews(): Promise<void>;
	}

}
declare module 'webdnn/graph_descriptor/graph_descriptor_webgpu' {
	/**
	 * @module webdnn
	 */
	/** Don't Remove This comment block */
	import { Placeholder } from 'webdnn/placeholder';
	import { GraphDescriptor } from 'webdnn/graph_descriptor/graph_descriptor';
	/**
	 * @protected
	 */
	export interface GraphDescriptorWebGPU extends GraphDescriptor {
	    kernel_source: string;
	    exec_infos: GraphDescriptorWebGPUExecInfos[];
	}
	/**
	 * @protected
	 */
	export interface GraphDescriptorWebGPUExecInfos {
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
declare module 'webdnn/descriptor_runner/descriptor_runner_webgpu' {
	import { GraphDescriptorWebGPU } from 'webdnn/graph_descriptor/graph_descriptor_webgpu';
	import SymbolicFloat32Array from 'webdnn/symbolic_typed_array/symbolic_float32array';
	import { BackendName } from 'webdnn/webdnn';
	import { DescriptorRunner, DescriptorRunnerOptions } from 'webdnn/descriptor_runner/descriptor_runner';
	/**
	 * DescriptorRunner for WebGPU
	 * @protected
	 */
	export default class DescriptorRunnerWebGPU extends DescriptorRunner<GraphDescriptorWebGPU, ArrayBuffer> {
	    constructor(options?: DescriptorRunnerOptions);
	    /**
	     * backend name
	     */
	    readonly backendName: BackendName;
	    /**
	     * WebGPU Handler
	     */
	    private webgpuHandler;
	    /**
	     * Static buffer, whose size and layout can be determined in compile time.
	     */
	    private staticBuffer;
	    /**
	     * Buffers whose size and layout cannot be determined without runtime information like image size (if it's dynamic).
	     */
	    private dynamicBuffer;
	    /**
	     * Buffers which contains metadata shared in each GPU kernel thread (ex. hyper parameters).
	     */
	    private metaBuffers;
	    /**
	     * Execution information such as each kernel size, input and output buffers, etc.
	     */
	    private executionInfos;
	    /**
	     * Return `true` if this backend is available in this environment.
	     * @returns {boolean}
	     */
	    static checkAvailability(): boolean;
	    /**
	     * Initialize descriptor runner asynchronously
	     * @returns {Promise<void>} Promise object which is resolved when the initialization finished.
	     */
	    init(): Promise<void>;
	    /**
	     * Check whether current GPU is supported or not. If it's not supported, an error is thrown.
	     * @returns {Promise<void>}
	     */
	    private checkIncompatibleGPU();
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
	    fetchDescriptor(directory: string): Promise<GraphDescriptorWebGPU>;
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
	    fetchParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    restoreCachedDescriptor(directory: string): Promise<GraphDescriptorWebGPU | null>;
	    /**
	     * Load cached descriptor from WebStorage
	     * @protected
	     */
	    restoreCachedParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer | null>;
	    /**
	     * save cache
	     */
	    saveCache(directory: string, descriptor: GraphDescriptorWebGPU, parameters: ArrayBuffer): Promise<void>;
	    setDescriptorAndParameters(descriptor: GraphDescriptorWebGPU, parameter: ArrayBuffer): Promise<void>;
	    /**
	     * Initialize static buffers, whose size and position can be determined in compile time.
	     *
	     * @param {ArrayBuffer} weightRawArray constant weight buffer
	     * @returns {Promise<void>}
	     */
	    private initializeStaticBuffer(weightRawArray);
	    /**
	     * Initialize meta buffers, which contains metadata shared in each GPU kernel thread (ex. hyper parameters).
	     * @returns {Promise<void>}
	     */
	    private initializeMetaBuffers();
	    /**
	     * Initialize dynamic buffers, whose size and position cannot be determined without runtime-information such as input image size
	     * (if it's dynamic).
	     * When all placeholder is resolved, this method is automatically called.
	     *
	     * @returns {Promise<void>}
	     */
	    private initializeDynamicBuffer();
	    /**
	     * Set actual value into placeholder. If all placeholder is resolved,
	     * [[DescriptorRunnerWebGPU#initializeDynamicBuffer|`initializeDynamicBuffer()`]] is automatically called.
	     *
	     * @param values mapping object of placeholder name and value
	     * @returns {Promise<void>}
	     */
	    setPlaceholderValue(values: {
	        [key: string]: number;
	    }): Promise<void>;
	    /**
	     * Get input [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]] object
	     *
	     * @returns array of input [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]]
	     * @deprecated Use [[webdnn.DescriptorRunner.inputs|`inputs`]] instead
	     */
	    getInputViews(): SymbolicFloat32Array[];
	    /**
	     * Get output [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]] object
	     *
	     * @returns array of output [[webdnn.SymbolicFloat32Array|`SymbolicFloat32Array`]]
	     * @deprecated Use [[webdnn.DescriptorRunner.outputs|`outputs`]] instead
	     */
	    getOutputViews(): SymbolicFloat32Array[];
	    /**
	     * Run descriptor. You must call [[webdnn.DescriptorRunner.getInputViews|`getInputViews`]] and
	     * [[webdnn.DescriptorRunner.getOutputViews|`getOutputViews`]] before calling this function.
	     */
	    run(): Promise<void>;
	}

}
declare module 'webdnn/image/enums' {
	/**
	 * @module webdnn/image
	 */
	/** Don't Remove This comment block */
	/**
	 * The data order
	 */
	export enum Order {
	    /** `[Channel, Height, Width]` format */
	    CHW = 0,
	    /** `[Height, Width, Channel]` format */
	    HWC = 1,
	}
	/**
	 * The color format
	 */
	export enum Color {
	    /** RGB format */
	    RGB = 0,
	    /** BGR format */
	    BGR = 1,
	    /** grey scale */
	    GREY = 2,
	    /** RGBA format */
	    RGBA = 3,
	    /** BGRA format */
	    BGRA = 4,
	}

}
declare module 'webdnn/image/canvas' {
	/**
	 * @module webdnn/image
	 */
	/** Don't Remove This comment block */
	/**
	 * Get canvas rendering context and check whether it is nonnull value.
	 *
	 * @param {CanvasRenderingContext2D} canvas
	 * @protected
	 */
	export function getContext2D(canvas: HTMLCanvasElement): CanvasRenderingContext2D;

}
declare module 'webdnn/image/image_data' {
	/**
	 * The rectangle of source position of image
	 */
	export interface SourceRect {
	    srcX?: number;
	    srcY?: number;
	    srcW?: number;
	    srcH?: number;
	}
	/**
	 * The rectangle of destination position of image
	 */
	export interface DestinationRect {
	    dstX?: number;
	    dstY?: number;
	    dstW?: number;
	    dstH?: number;
	}
	/**
	 * @protected
	 */
	export function getImageDataFromCanvas(canvas: HTMLCanvasElement, options?: SourceRect & DestinationRect): ImageData;
	/**
	 * @protected
	 */
	export function getImageDataFromDrawable(drawable: HTMLVideoElement | HTMLImageElement, options?: SourceRect & DestinationRect): ImageData;
	/**
	 * Return canvas `ImageData` object with specified scale.
	 *
	 * @param {HTMLCanvasElement | HTMLVideoElement | HTMLImageElement} image
	 * @param [options] Options
	 * @param {number} [options.srcX=0] left position of input clipping rect
	 * @param {number} [options.srcY=0] top position of input clipping rect
	 * @param {number} [options.srcW=canvas.width] width of input clipping rect
	 * @param {number} [options.srcH=canvas.height] height of input clipping rect
	 * @param {number} [options.dstW=options.srcW] width of output
	 * @param {number} [options.dstH=options.srcH] height of output
	 * @returns {ImageData}
	 * @protected
	 */
	export function getImageData(image: HTMLCanvasElement | HTMLVideoElement | HTMLImageElement, options?: SourceRect & DestinationRect): ImageData;
	/**
	 * @protected
	 */
	export function setImageDataToCanvas(imageData: ImageData, canvas: HTMLCanvasElement, options?: SourceRect & DestinationRect): void;

}
declare module 'webdnn/image/image_source' {
	/**
	 * @module webdnn/image
	 */
	/** Don't Remove This comment block */
	/**
	 * Load image of specified url
	 *
	 * @param {string} url the image url
	 * @returns {Promise<HTMLImageElement>} image element
	 */
	export function loadImageByUrl(url: string): Promise<HTMLImageElement>;
	/**
	 * Load image file selected in `<input type="file">` element.
	 *
	 * @param {HTMLInputElement} input the `<input type="file">` element
	 * @returns {Promise<HTMLImageElement>} image element
	 */
	export function loadImageFromFileInput(input: HTMLInputElement): Promise<HTMLImageElement>;
	/**
	 * Load image selected in file picker dialog
	 *
	 * Currently, web specification not supported the case if the dialog is canceled and no file is selected. In this case,
	 * the returned promise will never be resolved.
	 *
	 * @returns {Promise<HTMLImageElement>} image element
	 * @protected
	 */
	export function loadImageByDialog(): Promise<HTMLImageElement>;

}
declare module 'webdnn/image/image_array' {
	import { Color, Order } from 'webdnn/image/enums';
	import { DestinationRect, SourceRect } from 'webdnn/image/image_data';
	/**
	 * Option structure of [[webdnn/image.getImageArray|`WebDNN.Image.getImageArray`]]
	 */
	export interface ImageArrayOption {
	    /** Type of packed array */
	    type?: {
	        new (length: number): (Float32Array | Int32Array);
	    };
	    /** The color format */
	    color?: Color;
	    /** The data order */
	    order?: Order;
	    /** Bias value, which is parsed based on [[webdnn/image.ImageArrayOption.order|`order`]] value */
	    bias?: number[] | number;
	    /** Scale value, which is parsed based on [[webdnn/image.ImageArrayOption.order|`order`]] value */
	    scale?: number[] | number;
	}
	/**
	 * Types which are drawable at `HTMLCanvasElement`
	 */
	export type Drawable = HTMLImageElement | HTMLVideoElement | HTMLCanvasElement | ImageData;
	/**
	 * All type of image source which `WebDNN.Image` can be handled. For `string`, only the url of image resource is valid.
	 */
	export type ImageSource = string | HTMLInputElement | Drawable;
	/**
	 * Get image array as `{Float32 or Int32}ArrayBufferView` from ImageData object.
	 *
	 * @returns {ArrayBufferView} buffer with specified type
	 * @protected
	 */
	export function getImageArrayFromImageData(imageData: ImageData, options?: SourceRect & DestinationRect & ImageArrayOption): Float32Array | Int32Array;
	/**
	 * Get image array from canvas element as `{Float32 or Int32}ArrayBufferView`.
	 *
	 * @returns {ImageData} buffer with specified type
	 * @protected
	 */
	export function getImageArrayFromCanvas(canvas: HTMLCanvasElement, options?: SourceRect & DestinationRect & ImageArrayOption): Float32Array | Int32Array;
	/**
	 * Get image array from image element as `{Float32 or Int32}ArrayBufferView`.
	 *
	 * @returns {ImageData} buffer with specified type
	 * @protected
	 */
	export function getImageArrayFromDrawable(drawable: Drawable, options?: SourceRect & DestinationRect & ImageArrayOption): Float32Array | Int32Array;
	/**
	 * Create typed array by packing image data from image source with specified options.
	 *
	 * First, this method loads specified image resource. The behavior of this method depends on the `image` argument.
	 *
	 * - If `image` is an instance of `string`, it will be regarded as image url, and this method fetches that url.
	 *
	 * - If `image` is an instance of `HTMLInputElement`, it will be regarded as file input,
	 *   and this method loads the selected image file.
	 *
	 * - Otherwise, `image` will be regarded as drawable object.
	 *
	 * Then, loaded images are packed into typed array based on `options` argument.
	 *
	 * - The image is cropped based on [[SourceRect|`{srcX, srcY, srcW, srcH}`]].
	 *   As default, entire image is used.
	 *
	 * - The image is resized and translated into [[DestinationRect|`{dstX, dstY, dstW, dstH}`]].
	 *   As default, no resize and translation is performed.
	 *
	 * - [[ImageArrayOption.type|`options.type`]] is the type of packed typed array. As default, Float32Array is used.
	 *
	 * - [[ImageArrayOption.type|`options.color`]] is the color format of packed typed array. As default, [[Color.RGB|`RGB`]] is used.
	 *
	 * - [[ImageArrayOption.type|`options.order`]] is the data order of packed typed array. As default, [[Order.HWC|`HWC`]] is used.
	 *
	 * - [[ImageArrayOption.bias|`options.bias`]] is the bias value.
	 *   If specified, this method **subtracts** this value from original pixel value.
	 *
	 * - [[ImageArrayOption.scale|`options.scale`]] is the scale value. If specified, original pixel values are **divided** by this value.
	 *   [[ImageArrayOption.scale|`options.scale`]] and [[ImageArrayOption.bias|`options.bias`]] is used for converting pixel value `x` and
	 *   packed value `y` as follows:
	 *
	 *   - `y = (x - bias) / scale`
	 *   - `x = y * scale + bias`
	 *   - Note that color order is always RGB, not BGR.
	 *
	 * ### Examples
	 *
	 * - Load image of specified url
	 *
	 *   ```ts
	 *   let image = await WebDNN.Image.load('./cat.png');
	 *   ```
	 *
	 * - Load image selected in file input and resize it into 224 x 224
	 *
	 *   ```ts
	 *   let input = document.querySelector('input[type=file]');
	 *   let image = await WebDNN.Image.load(input, { dstW: 224, dstH: 224 });
	 *   ```
	 *
	 * - Load image data from canvas, normalize it into range `[-1, 1)`. In this case, normalized value `y` can be
	 *   calculated from pixel value `x` as follows: `y = (x - 128) / 128`.
	 *
	 *   ```ts
	 *   let canvas = document.getElementsByTagName('canvas')[0];
	 *   let image = await WebDNN.Image.load(canvas, { bias: [128, 128, 128], scale: [128, 128, 128] });
	 *   ```
	 *
	 * @param image please see above descriptions
	 * @param options please see above descriptions.
	 * @returns Created typed array
	 */
	export function getImageArray(image: ImageSource, options?: SourceRect & DestinationRect & ImageArrayOption): Promise<Float32Array | Int32Array>;
	/**
	 * Set image array data into canvas.
	 *
	 * ### Examples
	 *
	 * - Show DNN model's result
	 *
	 *   ```ts
	 *   let runner = await WebDNN.load('./model');
	 *   let output = runner.outputs[0];
	 *
	 *   await runner.run();
	 *
	 *   WebDNN.Image.setImageArrayToCanvas(output.toActual(), 256, 256, document.getElementById('canvas'))
	 *   ```
	 *
	 * - Generally image generation model's result contains noise pixel at their edge because of convolution's padding.
	 *   In follow example, these noise are cut off.
	 *
	 *   ```ts
	 *   WebDNN.Image.setImageArrayToCanvas(output, 256, 256, canvas, {
	 *      srcX: 16, srcY: 16, srcH: 256-16*2, srcW: 256-16*2, // Discard both ends 16px
	 *      dstW: 256, dstH: 256  // Resize cropped image into original output size.
	 *   });
	 *   ```
	 *
	 * @param array array which contains image data
	 * @param imageW width of image
	 * @param imageH height of image. The length of `array` must be `imageW * imageH * (# of channels)`
	 * @param canvas destination canvas
	 * @param options please see above descriptions and descriptions in [[webdnn/image.getImageArray|getImageArray()]].
	 *                `srcW` and `srcH` is ignored (overwritten by `imageW` and `imageH`).
	 */
	export function setImageArrayToCanvas(array: Float32Array | Int32Array, imageW: number, imageH: number, canvas: HTMLCanvasElement, options?: SourceRect & DestinationRect & ImageArrayOption): void;

}
declare module 'webdnn/image' {
	/**
	 * @module webdnn/image
	 * @preferred
	 *
	 * Module `WebDNN.Image` provides basic image processing operations like follows.
	 *
	 * - Load image by various way (File picker dialog, url string, canvas, video, etc.)
	 * - Pack image data into TypedArray
	 * - Crop and resize.
	 * - Show result on canvas element
	 *
	 */
	/** Don't Remove This comment block */
	export * from 'webdnn/image/enums';
	export * from 'webdnn/image/image_array';
	export * from 'webdnn/image/image_source';

}
declare module 'webdnn/math/argsort' {
	/**
	 * @module webdnn/math
	 */
	/** Don't Remove This comment block */
	/**
	 * Return indices of the top-K largest elements.
	 * This implementation is not stable sort.
	 *
	 * @param {number[]|Float32Array} arr array
	 * @param {number} k number of indices
	 * @returns {number[]} indices of top-K largest samples
	 */
	export function argmax(arr: number[] | Float32Array, k?: number): number[];
	/**
	 * Return indices of the top-K smallest elements.
	 * This implementation is not stable sort.
	 *
	 * @param {number[]|Float32Array|Int32Array} arr array
	 * @param {number} k number of indices
	 * @returns {number[]} indices of top-K smallest samples
	 */
	export function argmin(arr: number[] | Float32Array | Int32Array, k?: number): number[];

}
declare module 'webdnn/math' {
	/**
	 * @module webdnn/math
	 * @preferred
	 *
	 * Module `WebDNN.Math` provides basic mathematics operations for pre/post-processing.
	 */
	/** Don't Remove This comment block */
	export * from 'webdnn/math/argsort';

}
declare module 'webdnn/webdnn' {
	/// <reference path="webgpu.d.ts" />
	/**
	 * @module webdnn
	 * @preferred
	 *
	 * Module `WebDNN` provides main features of WebDNN.
	 */
	/** Don't Remove This comment block */
	import { DescriptorRunner as DescriptorRunnerGeneric } from 'webdnn/descriptor_runner/descriptor_runner';
	import { GraphDescriptor } from 'webdnn/graph_descriptor/graph_descriptor';
	import * as Image from 'webdnn/image';
	import * as Math from 'webdnn/math';
	/**
	 * get configuration
	 * @private
	 */
	export function getConfiguration<T>(key: string, defaultValue?: T): T;
	/**
	 * set configuration
	 * @private
	 */
	export function setConfiguration(key: string, value: any): void;
	/**
	 * Backend names supported in WebDNN
	 */
	export type BackendName = 'webgpu' | 'webgl' | 'webassembly' | 'fallback';
	/**
	 * Descriptor runner
	 */
	export type DescriptorRunner = DescriptorRunnerGeneric<GraphDescriptor, any>;
	/**
	 * Result structure of [[getBackendAvailability|`WebDNN.getBackendAvailability`]]
	 */
	export interface BackendAvailability {
	    /**
	     * Whether each backend is available or not.
	     *
	     * ### Example
	     *
	     * ```ts
	     * WebDNN.getBackendAvailability().status
	     * >>> {
	     *   'webgpu': false,
	     *   'webassembly': true,
	     *   'webgl': true,
	     *   'fallback': true
	     * }
	     * ```
	     */
	    status: {
	        [name in BackendName]: boolean;
	    };
	    /**
	     * Default backend order WebDNN try to use
	     *
	     * ### Examples
	     *
	     * ```ts
	     * WebDNN.getBackendAvailability().defaultOrder
	     * >>> ['webassembly', 'webgl', 'fallback']
	     * ```
	     */
	    defaultOrder: BackendName[];
	}
	/**
	 * Check each computing backend is available or not in this browser.
	 * The result will be returned as [[BackendAvailability|`BackendAvailability`]] structure.
	 *
	 * @returns backend availability
	 */
	export function getBackendAvailability(): BackendAvailability;
	/**
	 * Option structure of [[load|`WebDNN.load`]]
	 */
	export interface InitOption {
	    /**
	     * The order of backend names to be initialized.
	     */
	    backendOrder?: BackendName | (BackendName[]);
	    /**
	     * Backend-specific options. Currently (v1.3), this option has no effect.
	     */
	    backendOptions?: {
	        [key: string]: any;
	    };
	    /**
	     * Callback function which is called to notice the progress status of loading binary data.
	     *
	     * Currently Streaming fetch feature is not perfectly supported in browsers. Therefore, this option will be
	     * ignored in some web browsers.
	     *
	     * ### Examples
	     *
	     * ```js
	     * let runner = await WebDNN.load('./model', {
	     *     progressCallback: (loaded, total) => console.log(`${ (loaded/total*100).toFixed(1) }% Loaded`);
	     * });
	     * ```
	     */
	    progressCallback?: (loaded: number, total: number) => any;
	    /**
	     * URL of directory that contains weight binary files.
	     *
	     * If both
	     * [[InitOption.weightDirectory|`InitOption.weightDirectory`]] and
	     * [[InitOption.transformUrlDelegate|`InitOption.transformUrlDelegate`]] are specified,
	     * At first, all urls of binary weights' are replaced by [[InitOption.weightDirectory|`InitOption.weightDirectory`]], and then
	     * [[InitOption.transformUrlDelegate|`InitOption.transformUrlDelegate`]] are applied.
	     *
	     * ### Examples
	     *
	     * ```js
	     * // Graph descriptor JSON file will be loaded from 'original.host.com/model', and
	     * // model binary data will be loaded from 'custom.host.com/model'.
	     * WebDNN.load('https://original.host.com/model', {
	     *     weightDirectory: 'https://custom.host.com/model'
	     * });
	     * ```
	     */
	    weightDirectory?: string;
	    /**
	     * Delegate function which will be called with original url, and must return converted url strings.
	     * This function is called before WebDNN fetch any data (descriptor json file, and binary data)
	     * You can modified url to fetch data from other domain, for example.
	     *
	     * If both
	     * [[InitOption.weightDirectory|`InitOption.weightDirectory`]] and
	     * [[InitOption.transformUrlDelegate|`InitOption.transformUrlDelegate`]] are specified,
	     * At first, all urls of binary weights' are replaced by [[InitOption.weightDirectory|`InitOption.weightDirectory`]], and then
	     * [[InitOption.transformUrlDelegate|`InitOption.transformUrlDelegate`]] are applied.
	     *
	     * ### Examples
	     *
	     * Fetch binary data from other domain
	     *
	     * ```js
	     * // Graph descriptor JSON file will be loaded from 'original.host.com/model', and
	     * // model binary data will be loaded from 'custom.host.com/model'.
	     * WebDNN.load('https://original.host.com/model', {
	     *     transformUrlDelegate: (url) => {
	     *         if ((/\.bin/).test(url)) {
	     *             url = url.replace('original.host.com', 'custom.host.com');
	     *         }
	     *         return url;
	     *     }
	     * });
	     * ```
	     */
	    transformUrlDelegate?: (url: string) => string;
	    /**
	     * WebDNN cache strategy. One of follows is available.
	     *
	     * - `latest` (default)
	     *
	     *  Fetch `descriptor.json` at first and check whether assets in server is same as cached assets. If it's same, use cached assets,
	     *  otherwise, fetch all assets and replace cached assets.
	     *
	     * - `networkFirst`
	     *
	     *  Fetch all asset files. If it succeeds, use fetched assets. If failed, use cached assets if exist, otherwise, an error is thrown.
	     *
	     * - `cacheFirst`
	     *
	     *  If cache is exist, use cache, otherwise, fetch assets. If it failed, an error is thrown.
	     *
	     * - `networkOnly`
	     *
	     *  Fetch all asset files. If failed, an error is thrown.
	     *
	     * - `cacheOnly`
	     *
	     *  If cache is exist, use cache, otherwise, an error is thrown.
	     *
	     */
	    cacheStrategy?: 'latest' | 'networkFirst' | 'cacheFirst' | 'networkOnly' | 'cacheOnly';
	    /**
	     * If true, WebDNN save fetched parameter data cache in available `WebStorage`. As default, it's `true`.
	     */
	    saveCache?: boolean;
	}
	/**
	 * Initialize descriptor runner. This function performs follow things.
	 *
	 * 1. Try to initialize computing backend. WebDNN will try to initialize each backend in order of
	 *    the result of [[getBackendAvailability|`getBackendAvailability`]].
	 *    If you want to modify this order, specify [[InitOption.backendOrder|`initOption.backendOrder`]] option.
	 *
	 * 2. Load model data based on initialized backend. Generally, DNN binary data is very large and it takes long time to load.
	 *    [[InitOption.progressCallback|`initOption.progressCallback`]] option provides the progress status of loading.
	 *
	 * ### Examples
	 *
	 * - Basic usage
	 *
	 *   ```js
	 *   let runner = await WebDNN.load('./model');
	 *   ```
	 *
	 * - With `initOption.progressCallback` option
	 *
	 *   ```js
	 *   let runner = await WebDNN.load('./model', {
	 *       progressCallback: (loaded, total) => console.log(`${ (loaded/total*100).toFixed(1) }% Loaded`);
	 *   });
	 *   ```
	 *
	 * @param directory URL of directory that contains graph descriptor files (e.g. graph_webgpu.json)
	 * @param initOption Initialize option
	 * @return DescriptorRunner instance, which is the interface to input/output data and run the model.
	 */
	export function load(directory: string, initOption?: InitOption): Promise<DescriptorRunner>;
	export { GraphDescriptor };
	export { Math, Image };

}
declare module 'webdnn' {
	export * from 'webdnn/webdnn';
}
