/// <reference path="./matrix_base.ts" />
namespace WebDNN {
  export class MatrixCPU extends MatrixBase {
    data: Float32Array;

    constructor(shape: number[], data?: Float32Array, nocopy?: boolean) {
      super(shape);
      this.backend = 'cpu';
      if (nocopy) {
        this.data = data;
      } else if (data != null) {
        this.data = data.slice();
      } else {
        this.data = new Float32Array(this.size);
      }
    }

    // for debug purpose
    getScalar(index: number[]): number {
      if (index.length != this.ndim) {
        throw new Error('Dimension mismatch');
      }
      let offset: number = 0;
      for (let i = 0; i < this.ndim; i++) {
        offset += index[i] * this.strides[i];
      }
      return this.data[offset];
    }
  }
}
