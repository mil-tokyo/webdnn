///<reference path="./gpu_interface.ts" />
///<reference path="./gpu_interface_webgpu.ts" />
///<reference path="./gpu_interface_webassembly.ts" />
///<reference path="./gpu_interface_fallback.ts" />

namespace WebDNN {
    export let gpu: GPUInterface;

    let givenBackendOptions: { [key: string]: any };
    let tryingBackendOrder: string[];
    let loadedBackendName: string;

    async function tryInitNext(): Promise<string> {
        let backend_name = tryingBackendOrder.shift();
        if (!backend_name) {
            throw new Error('No backend is available');
        }

        let option = givenBackendOptions[backend_name];
        let gpuif: GPUInterface;
        try {
            switch (backend_name) {
                case 'webgpu':
                    gpuif = new GPUInterfaceWebGPU(option);
                    break;
                case 'webassembly':
                    gpuif = new GPUInterfaceWebassembly(option);
                    break;
                case 'fallback':
                    gpuif = new GPUInterfaceFallback(option);
                    break;
                default:
                    throw new Error('Unknown backend ' + backend_name);
            }
            await gpuif.init();
            gpu = gpuif;
            loadedBackendName = backend_name;
        } catch (ex) {
            console.error(`Failed to initialize ${backend_name} backend: ${ex}`);
            return await tryInitNext();
        }

        return loadedBackendName;
    }

    export async function init(backendOrder?: string | string[], backendOptions: { [key: string]: any } = {}): Promise<string> {
        if (!backendOrder) {
            backendOrder = ['webgpu', 'webassembly'];
        } else if (typeof backendOrder === 'string') {
            backendOrder = [backendOrder];
        }

        givenBackendOptions = backendOptions;
        tryingBackendOrder = backendOrder.concat(['fallback']);

        await tryInitNext();

        return loadedBackendName;
    }

    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param directory URL of directory that contains graph descriptor files (e.g. graph_fallback.json)
     * @param backendOrder The trying order of backend names to be initialized.
     * @return Interface to input/output data and run DNN.
     */
    export async function prepareAll(directory: string, backendOrder?: string | string[], backendOptions?: { [key: string]: any }): Promise<DNNInterface> {
        await init(backendOrder, backendOptions);

        while (true) {
            try {
                let runner = gpu.createDNNDescriptorRunner();
                await runner.load(directory);
                let input_views = await runner.getInputViews();
                let output_views = await runner.getOutputViews();

                return {
                    backendName: loadedBackendName, inputViews: input_views,
                    outputViews: output_views, run: runner.run.bind(runner)
                };
            } catch (ex) {
                console.error(`Model loading failed for ${loadedBackendName} backend. Trying next backend. ${ex.message}`);
                await tryInitNext();
            }
        }
    }

    /**
     * Interface to input/output data and run DNN.
     */
    export interface DNNInterface {
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
         * Run the DNN.
         */
        run: () => Promise<void>;
    }
}
