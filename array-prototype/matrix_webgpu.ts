/// <reference path="./matrix_gpu.ts" />

namespace WebDNN {
  export class MatrixWebGPU extends MatrixGPU {
    private static webgpuHandler: WebGPUHandler;
    webgpuBuffer: WebGPUBuffer;
    webgpuBufferView: Float32Array;

    constructor(shape: number[], data?: Float32Array) {
      super(shape);
      this.backend = 'webgpu';
      if (!data || data.length == 0) {
        data = new Float32Array(this.size || 1);//avoid 0byte buffer
      }
      this.webgpuBuffer = MatrixWebGPU.webgpuHandler.createBuffer(data);
      this.webgpuBufferView = new Float32Array(this.webgpuBuffer.contents);//can read / write GPU memory
    }

    static init(webgpuHandler: WebGPUHandler) {
      MatrixWebGPU.webgpuHandler = webgpuHandler;
    }

    async write(src: Float32Array, dst_offset?: number): Promise<void> {
      await MatrixWebGPU.webgpuHandler.sync();
      this.webgpuBufferView.set(src, dst_offset);
    }

    async read(dst: Float32Array = null, src_offset: number = 0, length?: number): Promise<Float32Array> {
      await MatrixWebGPU.webgpuHandler.sync();
      if (length === undefined) {
        length = this.webgpuBufferView.length - src_offset;
      }
      var src_view = new Float32Array(this.webgpuBufferView.buffer, this.webgpuBufferView.byteOffset + src_offset * Float32Array.BYTES_PER_ELEMENT, length);
      if (!dst) {
        dst = new Float32Array(src_view.length);
      }
      dst.set(src_view);
      return dst;
    }
  }
}
