/// <reference path="./matrix_base.ts" />
// abstract base class for GPU matrix

namespace WebDNN {
  export class MatrixGPU extends MatrixBase {
    constructor(shape: number[]) {
      super(shape);
    }

    // it seems some signature have to be different from MatrixCPU
    private dummy() {
      return;
    }
  }
}
