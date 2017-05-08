///<reference path="./gpu_interface.ts" />
///<reference path="./gpu_interface_webgpu.ts" />
///<reference path="./gpu_interface_webassembly.ts" />
///<reference path="./gpu_interface_fallback.ts" />

namespace WebDNN {
    export let gpu: GPUInterface;

    export async function init(backendOrder?: string | string[], backendOptions: { [key: string]: any } = {}): Promise<string> {
        let loaded_backend_name = '';
        if (!backendOrder) {
            backendOrder = ['webgpu', 'webassembly'];
        } else if (typeof backendOrder === 'string') {
            backendOrder = [backendOrder];
        }

        let backend_order_with_fb = backendOrder.concat(backendOrder, ['fallback']);
        for (let i = 0; i < backend_order_with_fb.length; i++) {
            let backend_name = backend_order_with_fb[i];
            let option = backendOptions[backend_name];
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
                loaded_backend_name = backend_name;
                break;
            } catch (ex) {
                console.error(`Failed to initialize ${backend_name} backend: ${ex}`);
            }
        }

        return loaded_backend_name;
    }

    /*
    Prepare backend interface and load model data at once
    */
    export async function prepareAll(directory: string, backend_order?: string | string[], backendOptions?: { [key: string]: any }): Promise<DNNInterface> {
        let backend_name = await init(backend_order, backendOptions);
        let runner = gpu.createDNNDescriptorRunner();
        await runner.load(directory);
        let input_views = await runner.getInputViews();
        let output_views = await runner.getOutputViews();
        return {
            backendName: backend_name, inputViews: input_views,
            outputViews: output_views, run: runner.run.bind(runner)
        };
    }

    export interface DNNInterface {
        backendName: string;
        inputViews: Float32Array[];
        outputViews: Float32Array[];
        run: () => Promise<void>;
    }
}
