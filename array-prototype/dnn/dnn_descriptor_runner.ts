namespace WebDNN {
  export class DNNDescriptorRunner {
    weightMat: DNNBufferWebGPU;
    dataMat: DNNBufferWebGPU;

    constructor(public descriptor: DNNDescriptor, private webGPUHandler: WebGPUHandler) {

    }

    async compile() {
      this.webGPUHandler.loadKernel(this.descriptor.kernel_source, 'descriptor');
      this.weightMat = new DNNBufferWebGPU(this.descriptor.weight_allocation.total_size * Float32Array.BYTES_PER_ELEMENT);
      this.dataMat = new DNNBufferWebGPU(this.descriptor.variable_allocation.total_size * Float32Array.BYTES_PER_ELEMENT);
      for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
        let exec_info = this.descriptor.exec_infos[i];
        let buf = new DNNBufferWebGPU(exec_info.meta_buffer.length * Float32Array.BYTES_PER_ELEMENT);
        await buf.write(new Uint8Array(exec_info.meta_buffer));
        exec_info.meta_buffer_gpu_buffer = buf;
      }
    }

    async loadWeights(weightsData: Float32Array) {
      await this.weightMat.write(weightsData);
    }

    async run(inputs: Float32Array[]): Promise<Float32Array[]> {
      //set input to GPU
      for (let i = 0; i < this.descriptor.inputs.length; i++) {
        let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.inputs[i]];
        await this.dataMat.write(inputs[i], var_alloc.offset);
      }

      //execute kernels
      for (let i = 0; i < this.descriptor.exec_infos.length; i++) {
        let exec_info = this.descriptor.exec_infos[i];
        this.webGPUHandler.executeSinglePipelineState(
          'descriptor.' + exec_info.entry_func_name,
          exec_info.threadgroups_per_grid,
          exec_info.threads_per_thread_group,
          [this.weightMat, this.dataMat, exec_info.meta_buffer_gpu_buffer]
        );
      }

      // get output from GPU
      let outputs: Float32Array[] = [];
      for (let i = 0; i < this.descriptor.outputs.length; i++) {
        let var_alloc = this.descriptor.variable_allocation.allocation[this.descriptor.outputs[i]];
        let output_array = new Float32Array(var_alloc.size);
        await this.dataMat.read(output_array, var_alloc.offset, var_alloc.size);
        outputs.push(output_array);
      }

      return outputs;
    }
  }

  export interface DNNDescriptor {
    kernel_source: string;
    exec_infos: DNNDescriptorExecInfos[];
    weight_allocation: {total_size: number;
    allocation: {[index: string]: {name: string, offset: number, size: number}}};
    variable_allocation: {total_size: number;
    allocation: {[index: string]: {name: string, offset: number, size: number}}};
    inputs: string[];
    outputs: string[];
  }

  export interface DNNDescriptorExecInfos {
    entry_func_name: string;
    threadgroups_per_grid: WebGPUSize;
    threads_per_thread_group: WebGPUSize;
    meta_buffer: number[];
    meta_buffer_gpu_buffer: DNNBufferWebGPU;
  }
}
