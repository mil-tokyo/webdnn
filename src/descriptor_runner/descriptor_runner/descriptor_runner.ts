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
export interface DescriptorRunnerConstructor<D extends GraphDescriptor, P> {
    new(option?: any): DescriptorRunner<D, P>

    checkAvailability(): boolean;
}

/**
 * `DescriptorRunner` provides interface to execute DNN model and access input and output buffers.
 */
export abstract class DescriptorRunner<D extends GraphDescriptor, P> {
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
     * backend name
     * @type {string}
     */
    readonly backendName: BackendName;

    /**
     * descriptor
     * @type {null}
     */
    protected descriptor: D | null = null;

    /**
     * placeholder context which manages all placeholders and their values
     */
    protected placeholderContext: PlaceholderContext | null;

    /**
     * Return `true` if this backend is available in this environment.
     * @returns {boolean}
     */
    static checkAvailability() {
        return false;
    }

    /**
     * Initialize descriptor runner asynchronously
     * @returns {Promise<void>} Promise object which is resolved when the initialization finished.
     */
    abstract async init(): Promise<void>;

    /**
     * set graph descriptor and parameters
     * @protected
     */
    abstract async setDescriptorAndParameters(descriptor: D, parameters: P): Promise<void>;

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
    abstract async fetchDescriptor(directory: string): Promise<D>;

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
    abstract async fetchParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<P>;

    /**
     * Load cached descriptor from WebStorage
     * @protected
     */
    abstract async restoreCachedDescriptor(directory: string): Promise<D | null>

    /**
     * Load cached descriptor from WebStorage
     * @protected
     */
    abstract async restoreCachedParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<P | null>;

    /**
     * save cache
     * @protected
     */
    abstract async saveCache(directory: string, descriptor: D, parameters: P): Promise<void>;

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
}
