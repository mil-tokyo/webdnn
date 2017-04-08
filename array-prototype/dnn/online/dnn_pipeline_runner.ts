namespace WebDNN {
  export class DNNPipelineRunner {
    dnnPipelineData: DNNPipelineData;
    webgpuHandler: WebGPUHandler;
    weightMat: MatrixWebGPU;
    dataMat: MatrixWebGPU;

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
      this.weightMat = new MatrixWebGPU([this.dnnPipelineData.weightBuffersAssignment.totalSize]);
      this.dataMat = new MatrixWebGPU([this.dnnPipelineData.dataBuffersAssignment.totalSize]);
    }

    loadWeights(mats: MatrixCPU[]) {
      //TODO
    }

    async run(inputs: MatrixCPU[], inputIndices: number[], outputIndices: number[]) {
      //set input to GPU
      for (let i = 0; i < inputIndices.length; i++) {
        let input_index = inputIndices[i];
        let offset = this.dnnPipelineData.dataBuffersAssignment.buffers[input_index].offset;
        await this.dataMat.write(inputs[i].data, offset);
      }

      //execute kernels
      for (let i = 0; i < this.dnnPipelineData.kernels.length; i++) {
        let kernel = this.dnnPipelineData.kernels[i];
        let kernel_namespace = 'pipeline_' + i;
        let kernel_name = kernel_namespace + '.' + kernel.kernelFunctionName;
        console.log(`running lernel ${kernel_name}`);
        this.webgpuHandler.executeSinglePipelineState(kernel_name,
          kernel.threadgroupsPerGrid, kernel.threadsPerThreadgroup,
          [this.weightMat, this.dataMat]);
      }

      //get output from GPU
      let outputs: MatrixCPU[] = [];
      for (let i = 0; i < outputIndices.length; i++) {
        let output_index = outputIndices[i];
        let buf_info = this.dnnPipelineData.dataBuffersAssignment.buffers[output_index];
        let output_array = await this.dataMat.read(null, buf_info.offset, buf_info.size);
        outputs.push(new MatrixCPU(buf_info.shape, output_array, true));
      }

      return outputs;
    }
  }
}
