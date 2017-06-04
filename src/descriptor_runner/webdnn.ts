///<reference path="./gpu_interface/gpu_interface.ts" />
///<reference path="./gpu_interface/gpu_interface_webgpu.ts" />
///<reference path="./gpu_interface/gpu_interface_webassembly.ts" />
///<reference path="./gpu_interface/gpu_interface_fallback.ts" />

namespace WebDNN {
    export const backends = {
        'webgpu': GPUInterfaceWebGPU,
        'webassembly': GPUInterfaceWebassembly,
        'fallback': GPUInterfaceFallback,
    };

    export let gpu: GPUInterface<GraphDescriptor, DescriptorRunner<GraphDescriptor>> | null;
    export let backendName: string = 'none';

    async function initBackend(backendName: string, option?: any) {
        if (!(backendName in backends)) throw new Error(`Unknown backend: "${backendName}"`);

        let gpu: GPUInterface<GraphDescriptor, DescriptorRunner<GraphDescriptor>>;

        try {
            gpu = new backends[backendName](option);
            await gpu.init();
        } catch (ex) {
            console.warn(`Failed to initialize ${backendName} backend: ${ex}`);
            return false;
        }

        WebDNN.gpu = gpu;
        WebDNN.backendName = backendName;

        return true;
    }

    export async function init(backendOrder?: string | string[], backendOptions: { [key: string]: any } = {}): Promise<string> {
        if (!backendOrder) {
            backendOrder = ['webgpu', 'webassembly'];
        } else if (typeof backendOrder === 'string') {
            backendOrder = [backendOrder];
        }

        backendOrder = backendOrder.slice();
        if (backendOrder.indexOf('fallback') === -1) backendOrder.concat(['fallback']);

        while (backendOrder.length > 0) {
            let backendName = backendOrder.shift()!;

            if (await initBackend(backendName, backendOptions[backendName])) return WebDNN.backendName;
        }

        throw new Error('No backend is available');
    }

    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param backendOrder The trying order of backend names to be initialized.
     * @param backendOptions Backend options.
     * @param progressCallback callback which is called to notice the loading is progressing.
     */
    export interface InitOption {
        backendOrder?: string | string[],
        backendOptions?: { [key: string]: any },
        progressCallback?: (loaded: number, total: number) => any
    }

    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param directory URL of directory that contains graph descriptor files (e.g. graph_fallback.json)
     * @param initOption Initialize option
     * @return Interface to input/output data and run the model.
     */
    export async function prepareAll(directory: string, initOption: InitOption = {}): Promise<GraphInterface> {
        let backendOrder = initOption.backendOrder;
        if (!backendOrder) {
            backendOrder = ['webgpu', 'webassembly'];
        } else if (typeof backendOrder === 'string') {
            backendOrder = [backendOrder];
        }
        backendOrder = backendOrder.slice();
        if (backendOrder.indexOf('fallback') === -1) backendOrder.concat(['fallback']);

        let backendOptions = initOption.backendOptions || {};

        while (backendOrder.length > 0) {
            let backendName = backendOrder.shift()!;
            if (!(await initBackend(backendName, backendOptions[backendName]))) continue;

            let runner = gpu!.createDescriptorRunner();

            try {
                await runner.load(directory, initOption.progressCallback);
            } catch (ex) {
                console.warn(`Model loading failed for ${backendName} backend. Trying next backend: ${ex.message}`);
            }

            let inputViews = await runner.getInputViews();
            let outputViews = await runner.getOutputViews();

            return {
                backendName: backendName,
                inputViews: inputViews,
                outputViews: outputViews,
                run: runner.run.bind(runner)
            };
        }

        throw new Error('No backend is available');
    }

    /**
     * Interface to input/output data and run the model.
     */
    export interface GraphInterface {
        /**
         * The name of backend.
         */
        backendName: string;
        /**
         * The buffers to write input data.
         */
        inputViews: Float32Array[];
        /**
         * The buffers to read output data.
         */
        outputViews: Float32Array[];
        /**
         * Run the model.
         */
        run: () => Promise<void>;
    }
}
