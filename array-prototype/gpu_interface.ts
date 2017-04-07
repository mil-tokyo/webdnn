// interface for $M.gpu

namespace WebDNN {
  export interface GPUInterface {
    init(option?: any): Promise<null>;
    toGPU(m: MatrixCPU): MatrixGPU;
    toCPU(m: MatrixGPU): Promise<MatrixCPU>;

    add(a: MatrixGPU, b: MatrixGPU): MatrixGPU;
    sub(a: MatrixGPU, b: MatrixGPU): MatrixGPU;
    mul(a: MatrixGPU, b: MatrixGPU): MatrixGPU;
    div(a: MatrixGPU, b: MatrixGPU): MatrixGPU;
  }
}
