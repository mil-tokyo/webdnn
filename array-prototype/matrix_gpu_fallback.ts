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
  }
}
