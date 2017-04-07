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

    // async: there may be platforms synchronization is needed before writing
    async write(src: Float32Array, dst_offset?: number): Promise<void> {
      throw new Error();
    }

    async read(dst: Float32Array, src_offset?: number, length?: number): Promise<Float32Array> {
      throw new Error();
    }
  }
}
