namespace WebDNN {
  export class DNN {
    static webgpuHandler: WebGPUHandler;
    dnnPipeline: DNNPipeline;
    
    constructor() {
      this.dnnPipeline = new DNNPipeline();
      this.dnnPipeline.operations = [];
      this.dnnPipeline.operations.push(new DNNMalloc("myout", [4]));
      var relu = new ReluLayer(new DNNLayerIONames(["myin"], ["myout"]), {'size': 4});
      this.dnnPipeline.operations.push(relu.getKernel(1));
      this.dnnPipeline.operations.push(new DNNFree("myin"));

    }

    async run() {
      let myin = new MatrixCPU([4], new Float32Array([1.0, 2.0, -1.0, 5.0]));
      let inVars = new Map([['myin', myin]]);
      let outVars = await this.dnnPipeline.run(inVars, this);
      console.log(outVars.get('myout').data);
    }
  }
}
