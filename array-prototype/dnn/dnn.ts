namespace WebDNN {
  export class DNN {
    static webgpuHandler: WebGPUHandler;
    dnnPipeline: DNNPipeline;
    
/*    constructor() {
      this.dnnPipeline = new DNNPipeline();
      this.dnnPipeline.operations = [];
      this.dnnPipeline.operations.push(new DNNMalloc("myout", [4]));
      var relu = new ReluLayer(new DNNLayerIONames(["myin"], ["myout"]), {'size': 4});
      Array.prototype.push.apply(this.dnnPipeline.operations, relu.getKernel(1));
      this.dnnPipeline.operations.push(new DNNFree("myin"));

    }

    async run() {
      let myin = new MatrixCPU([4], new Float32Array([1.0, 2.0, -1.0, 5.0]));
      let inVars = new Map([['myin', myin]]);
      let outVars = await this.dnnPipeline.run(inVars, this);
      console.log(outVars.get('myout').data);
    }*/
    
    constructor() {
      this.dnnPipeline = new DNNPipeline();
      this.dnnPipeline.operations = [];
/*      this.dnnPipeline.operations.push(new DNNMalloc("myout", [1, 2]));
      var fc = new FullyConnectedLayer(new DNNLayerIONames(["myin"], ["myout"], ['fc_weight', 'fc_bias']), {'inDim': 3, 'outDim': 2});
      Array.prototype.push.apply(this.dnnPipeline.operations, fc.getKernel(1));
      this.dnnPipeline.operations.push(new DNNFree("myin"));

      var fc_weight = new MatrixCPU([3, 2], new Float32Array([0.1, 0.3, 0.5, 0.7, 0.9, 1.1]));
      var fc_bias = new MatrixCPU([2], new Float32Array([1.0, -1.0]));
      this.dnnPipeline.setWeights(new Map([['fc_weight', fc_weight], ['fc_bias', fc_bias]]));*/
    }

    async run() {
      let myin = new MatrixCPU([1, 3], new Float32Array([1.0, 2.0, -1.0]));
      let inVars = new Map([['myin', myin]]);
      let outVars = await this.dnnPipeline.run(inVars, this);
      console.log(outVars.get('myout').data);
    }
  }
}
