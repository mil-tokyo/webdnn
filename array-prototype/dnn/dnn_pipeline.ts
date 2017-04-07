namespace WebDNN {
  type DNNPipelineItem = DNNPrimitiveKernel | DNNMalloc | DNNFree;
  export class DNNMalloc {
    name: string;
    shape: number[];
    constructor(name: string, shape: number[]) {
      this.name = name;
      this.shape = shape;
    }

    run(dnn: DNN, flowVars: Map<string, MatrixWebGPU>) {
      if (flowVars.has(this.name)) {
        throw new Error(`Variable ${this.name} already exists`);
      }
      flowVars.set(this.name, new MatrixWebGPU(this.shape));
    }
  }

  export class DNNFree {
    name: string;
    constructor(name: string) {
      this.name = name;
    }

    run(dnn: DNN, flowVars: Map<string, MatrixWebGPU>) {
      if (!flowVars.has(this.name)) {
        throw new Error(`Variable ${this.name} not exists`);
      }

      flowVars.delete(this.name);
    }

  }
  export class DNNPipeline {
    operations: DNNPipelineItem[];
    weightsGPU: Map<string, MatrixWebGPU>;

    setWeights(weights: Map<string, MatrixCPU>) {
      this.weightsGPU = new Map();
      weights.forEach((value, key) => {
        this.weightsGPU.set(key, <MatrixWebGPU>WebDNN.gpu.toGPU(value));
      });
    }

    async run(inVars: Map<string, MatrixCPU>, dnn: DNN): Promise<Map<string, MatrixCPU> > {
      let flowVars: Map<string, MatrixWebGPU> = new Map();
      inVars.forEach((value, key) => {
        flowVars.set(key, <MatrixWebGPU>WebDNN.gpu.toGPU(value));
      });

      this.operations.forEach((operation) => {
        if (operation instanceof DNNMalloc) {
          operation.run(dnn, flowVars);
        } else if (operation instanceof DNNFree) {
          operation.run(dnn, flowVars);
        } else if (operation instanceof DNNPrimitiveKernel) {
          operation.run(dnn, this, flowVars);
        } else {
          throw new Error('Unknown pipeline operation');
        }
      });

      let outVars: Map<string, MatrixCPU> = new Map();
      var outNames = Array.from(flowVars.keys());
      for (let i = 0; i < outNames.length; i++) {
        let outName = outNames[i];
        outVars.set(outName, await WebDNN.gpu.toCPU(flowVars.get(outName)));
      }
      flowVars.clear();

      return outVars;
    }
  }
}
