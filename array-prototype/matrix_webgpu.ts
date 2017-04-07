namespace WebDNN {
  export class MatrixWebGPU extends MatrixGPU {
    private static webgpuHandler: WebGPUHandler;
    webgpuBuffer: WebGPUBuffer;

    constructor(shape: number[], data?: Float32Array) {
      super(shape);
      this.backend = 'webgpu';
      if (!data || data.length == 0) {
        data = new Float32Array(this.size || 1);//avoid 0byte buffer
      }
      this.webgpuBuffer = MatrixWebGPU.webgpuHandler.createBuffer(data);
    }

    static init(webgpuHandler: WebGPUHandler) {
      MatrixWebGPU.webgpuHandler = webgpuHandler;
    }
  }
}
