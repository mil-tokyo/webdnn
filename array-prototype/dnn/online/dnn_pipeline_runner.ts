namespace WebDNN {
  export class DNNPipelineRunner {
    dnnPipelineData: DNNPipelineData;
    webgpuHandler: WebGPUHandler;
    weightMat: DNNBufferWebGPU;
    dataMat: DNNBufferWebGPU;

    constructor(dnnPipelineData: DNNPipelineData, webgpuHandler: WebGPUHandler) {
      this.dnnPipelineData = dnnPipelineData;
      this.webgpuHandler = webgpuHandler;
    }

    compile() {
      for (let i = 0; i < this.dnnPipelineData.kernels.length; i++) {
        let kernel = this.dnnPipelineData.kernels[i];
        let kernel_namespace = 'pipeline_' + i;
        this.webgpuHandler.loadKernel(kernel.kernelString, kernel_namespace);
      }
      this.weightMat = new DNNBufferWebGPU(this.dnnPipelineData.weightBuffersAssignment.totalSize * Float32Array.BYTES_PER_ELEMENT);
      this.dataMat = new DNNBufferWebGPU(this.dnnPipelineData.dataBuffersAssignment.totalSize * Float32Array.BYTES_PER_ELEMENT);
    }

    async loadWeights(weightsData: Float32Array) {
      await this.weightMat.write(weightsData);
    }

    async run(inputs: Float32Array[]): Promise<Float32Array[]> {
      //set input to GPU
      for (let i = 0; i < this.dnnPipelineData.inputs.length; i++) {
        let input_index = this.dnnPipelineData.inputs[i];
        let offset = this.dnnPipelineData.dataBuffersAssignment.buffers[input_index].offset;
        await this.dataMat.write(inputs[i], offset);
      }

      //execute kernels
      for (let i = 0; i < this.dnnPipelineData.kernels.length; i++) {
        let kernel = this.dnnPipelineData.kernels[i];
        let kernel_namespace = 'pipeline_' + i;
        let kernel_name = kernel_namespace + '.' + kernel.kernelFunctionName;
        this.webgpuHandler.executeSinglePipelineState(kernel_name,
          kernel.threadgroupsPerGrid, kernel.threadsPerThreadgroup,
          [this.weightMat, this.dataMat]);
      }

      //get output from GPU
      let outputs: Float32Array[] = [];
      for (let i = 0; i < this.dnnPipelineData.outputs.length; i++) {
        let output_index = this.dnnPipelineData.outputs[i];
        let buf_info = this.dnnPipelineData.dataBuffersAssignment.buffers[output_index];
        let output_array = new Float32Array(buf_info.size);
        await this.dataMat.read(output_array, buf_info.offset, buf_info.size);
        outputs.push(output_array);
      }

      return outputs;
    }
  }
}
