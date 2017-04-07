/// <reference path="./matrix_gpu.ts" />
// implemented in pure js, but act like GPU matrix

namespace WebDNN {
  export class MatrixGPUFallback extends MatrixGPU {
    data: Float32Array;
    constructor(shape: number[], data?: Float32Array, nocopy?: boolean) {
      super(shape);
      this.backend = 'gpufallback';
      if (nocopy) {
        this.data = data;
      } else if (data != null) {
        this.data = data.slice();
      } else {
        this.data = new Float32Array(this.size);
      }
    }

    async write(src: Float32Array, dst_offset?: number): Promise<void> {
      this.data.set(src, dst_offset);
    }

    async read(dst: Float32Array = null, src_offset: number = 0, length?: number): Promise<Float32Array> {
      if (length === undefined) {
        length = this.data.length - src_offset;
      }
      var src_view = new Float32Array(this.data.buffer, this.data.byteOffset + src_offset * Float32Array.BYTES_PER_ELEMENT, length);
      if (!dst) {
        dst = new Float32Array(src_view.length);
      }
      dst.set(src_view);
      return dst;
    }
  }
}
