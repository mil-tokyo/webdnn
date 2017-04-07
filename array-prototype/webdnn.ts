namespace WebDNN {
  export var gpu: GPUInterface = null;

  export async function init(backend?: string, backend_option?: any): Promise<string> {
    let webgpuif = new GPUInterfaceWebGPU();
    try {
      await webgpuif.init();
      gpu = webgpuif;
      DNN.webgpuHandler = webgpuif.webgpuHandler;
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
