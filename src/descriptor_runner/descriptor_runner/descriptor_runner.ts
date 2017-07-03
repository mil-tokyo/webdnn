/// <reference path="../graph_descriptor/graph_descriptor.ts" />
/// <reference path="../placeholder.ts" />
/// <reference path="../symbolic_array_buffer_view.ts" />

namespace WebDNN {
    /**
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
    export abstract class DescriptorRunner<D extends GraphDescriptor> {
        readonly backendName: string;
        protected _running: boolean = false;
        descriptor: D | null = null;
        placeholderContext: PlaceholderContext | null;
        ignoreCache: boolean = false;

        /**
         * Initialize this runner
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
         */
        abstract async load(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<void>;

        /**
         * Set actual value into placeholders. If no placeholder is exist in graph descriptor, it's no need to call this function.
         */
        abstract async setPlaceholderValue(values: { [key: string]: number }): Promise<void>;

        /**
         * Get input ArrayBufferView object
         */
        abstract getInputViews(): SymbolicFloat32Array[];

        /**
         * Get output ArrayBufferView object
         */
        abstract getOutputViews(): SymbolicFloat32Array[];

        /**
         * Run descriptor. You must call [[getInputViews]] and [[getOutputViews]] before calling this function.
         */
        abstract async run(): Promise<void>;

        /**
         * Get if model is running.
         * While running, calling run() again or modifying input is invalid.
         */
        get running(): boolean {
            return this._running;
        }
    }
}
