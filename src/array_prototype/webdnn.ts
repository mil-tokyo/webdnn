///<reference path="./gpu_interface.ts" />
///<reference path="./gpu_interface_webgpu.ts" />
///<reference path="./gpu_interface_fallback.ts" />

namespace WebDNN {
    export let gpu: GPUInterface;

    export async function init(backend?: string, backendOption?: any): Promise<string> {
        let webgpuif = new GPUInterfaceWebGPU(backendOption);
        try {
            await webgpuif.init();
            gpu = webgpuif;
            backend = 'webgpu';
        } catch (e) {
            console.error('Failed to initialize WebGPU backend; fallback to pure js backend. Error=' + e.toString());
            let gpufbif = new GPUInterfaceFallback();
            await gpufbif.init();
            gpu = gpufbif;
            backend = 'fallback';
        }

        return backend;
    }
}
