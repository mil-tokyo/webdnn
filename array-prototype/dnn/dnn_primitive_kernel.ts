namespace WebDNN {

  export class DNNPrimitiveKernel {
    ioNames: DNNLayerIONames;
    metaInts: number[];
    metaFloats: number[];
    threadgroupsPerGrid: WebGPUSize;
    threadsPerThreadgroup: WebGPUSize;
    kernelFunctionName: string;

    run(dnn: DNN, dnnPipeline: DNNPipeline, flowVars: Map<string, MatrixWebGPU>) {
      let metaIntsBuf = DNN.webgpuHandler.createBuffer(new Int32Array(this.metaInts));
      let metaFloatsBuf = DNN.webgpuHandler.createBuffer(new Float32Array(this.metaFloats));
      let buffers: (WebGPUBuffer | MatrixWebGPU)[] = [];
      buffers.push(metaIntsBuf);
      buffers.push(metaFloatsBuf);
      this.ioNames.inputs.forEach((name) => { buffers.push(flowVars.get(name)); });
      this.ioNames.outputs.forEach((name) => { buffers.push(flowVars.get(name)); });
      this.ioNames.weights.forEach((name) => { buffers.push(dnnPipeline.weightsGPU.get(name)); });
      DNN.webgpuHandler.executeSinglePipelineState(this.kernelFunctionName,
        this.threadgroupsPerGrid, this.threadsPerThreadgroup, buffers);
    }
  }
}
