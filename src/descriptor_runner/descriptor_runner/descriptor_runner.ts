/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { GraphDescriptor } from "../graph_descriptor/graph_descriptor";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import { BackendName } from "../webdnn";

/**
 * @protected
 */
export interface DescriptorRunnerConstructor<D extends GraphDescriptor> {
    new(option?: any): DescriptorRunner<D>

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

    protected _running: boolean = false;

    protected descriptor: D | null = null;

    protected placeholderContext: PlaceholderContext | null;

    /**
     * @protected
     */
    ignoreCache: boolean = false;


    /**
     * Initialize this runner
     *
     * @protected
     */
    abstract async init(): Promise<void>;

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
    abstract async load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;

    /**
     * Set actual value into placeholders. If no placeholder is exist in graph descriptor, it's no need to call this function.
     *
     * @param values dictionary object of placeholder name and value pair
     * @protected
     */
    abstract async setPlaceholderValue(values: { [key: string]: number }): Promise<void>;

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
    abstract async run(): Promise<void>;

    /**
     * Return `true` if model is running.
     * While running, calling run() again or modifying input is invalid.
     */
    get running(): boolean {
        return this._running;
    }
}
