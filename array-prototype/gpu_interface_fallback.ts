namespace WebDNN {
  export class GPUInterfaceFallback implements GPUInterface {

    async init(option?: any) {
      // TODO: initialize functions
    }

    toGPU(m: MatrixCPU): MatrixGPU {
      let ans = new MatrixGPUFallback(m.shape, m.data);
      return ans;
    }

    async toCPU(m: MatrixGPUFallback): Promise<MatrixCPU> {
      let ans = new MatrixCPU(m.shape, m.data);
      return ans;
    }

    add(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback {
      return WebDNN.add(a, b);
    }
  }
}
