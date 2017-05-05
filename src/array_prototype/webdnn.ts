///<reference path="./gpu_interface.ts" />
///<reference path="./gpu_interface_webgpu.ts" />
///<reference path="./gpu_interface_webassembly.ts" />
///<reference path="./gpu_interface_fallback.ts" />

namespace WebDNN {
    export let gpu: GPUInterface;

    export async function init(backend?: string, backendOption?: any): Promise<string> {
        let backend_loaded = false;
        let loaded_backend_name = 'fallback';
        if (!backend || backend == 'webgpu') {
            try {
                let webgpuif = new GPUInterfaceWebGPU(backendOption);
                await webgpuif.init();
                gpu = webgpuif;
                loaded_backend_name = 'webgpu';
                backend_loaded = true;
            } catch (e) {
                console.error('Failed to initialize WebGPU backend. Error=' + e.toString());
            }
        }

        if ((!backend && !backend_loaded) || backend == 'webassembly') {
            try {
                let webassemblyif = new GPUInterfaceWebassembly(backendOption);
                await webassemblyif.init();
                gpu = webassemblyif;
                loaded_backend_name = 'webassembly';
                backend_loaded = true;
            } catch (e) {
                console.error('Failed to initialize Webassembly backend. Error=' + e.toString());
            }
        }

        if (backend == 'fallback') {
            // use fallback backend explicitly
        } else if (!backend_loaded) {
            console.error('Unknown backend.');
        }

        if (!backend_loaded) {
            let gpufbif = new GPUInterfaceFallback(backendOption);
            await gpufbif.init();
            gpu = gpufbif;
            backend_loaded = true;
        }
        console.info(`Initialized ${loaded_backend_name} backend.`);

        return loaded_backend_name;
    }
}
