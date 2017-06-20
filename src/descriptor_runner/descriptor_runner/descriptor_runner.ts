/// <reference path="../graph_descriptor/graph_descriptor.ts" />
/// <reference path="../placeholder.ts" />
/// <reference path="../symbolic_array_buffer_view.ts" />

namespace WebDNN {
    /**
     * `DescriptorRunner` executes computation based on `GraphDescriptor`.
     */
    export abstract class DescriptorRunner<D extends GraphDescriptor> {
        readonly backendName: string;
        descriptor: D | null = null;
        placeholderContext: PlaceholderContext | null;
        ignoreCache: boolean = false;

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

        abstract setPlaceholderValue(placeholders: { [key: string]: number }): void;

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
