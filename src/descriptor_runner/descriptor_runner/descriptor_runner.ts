/// <reference path="../graph_descriptor/graph_descriptor.ts" />

namespace WebDNN {
    /**
     * `DescriptorRunner` executes computation based on `GraphDescriptor`.
     *
     * 1. runner.init()
     *      Initialize runner.
     *
     * 2. runner.load()
     *      Load graph descriptor.
     *      In this process, follow operations are automatically called.
     *
     *      - runner.compile()
     *          Compile the kernels
     *
     *      - runner.initStaticBuffer()
     *          Initialize static buffer which is independent from placeholders.
     *
     * 3. runner.setPlaceholder()
     *      Set values into place.
     *      In this process, follow operations are automatically called.
     *
     *      - runner.initDynamicBuffer()
     *          Initialize dynamic buffer which is dependent on placeholders.
     *
     * 4. runner.run()
     *
     *
     */
    export abstract class DescriptorRunner<D extends GraphDescriptor> {
        readonly backendName: string;
        descriptor: D | null = null;
        ignoreCache: boolean = false;

        constructor(option?: any) {

        }

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

        abstract setPlaceholder(placeholders: { [key: string]: number }): void;

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
        abstract getInputViews(): Promise<BufferView[]>;

        /**
         * Get output ArrayBufferView object
         */
        abstract getOutputViews(): Promise<BufferView[]>;
    }
}
