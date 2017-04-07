namespace WebDNN {
  export class DNNLayer {
    ioNames: DNNLayerIONames;
    constructor(ioNames: DNNLayerIONames) {
      this.ioNames = ioNames;
    }

    getKernel(batchSize: number): DNNPrimitiveKernel[] {
      throw new Error();
    }
  }
}
