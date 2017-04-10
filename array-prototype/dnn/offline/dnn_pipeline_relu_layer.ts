namespace WebDNN {
  export class DNNPipelineReluLayer implements DNNPipelineLayer {
    constructor(params: any) {
    }

    getKernels(ioBuffer: DNNPipelineLayerIOBuffer): DNNPipelineKernel[] {
      let kernel_string = `
#include <metal_stdlib>
using namespace metal;

#define INPUT_OFFSET ${ioBuffer.bottoms[0].offset}
#define OUTPUT_OFFSET ${ioBuffer.tops[0].offset}
#define N ${ioBuffer.tops[0].size}

kernel void relu(const device float *weight_buffer[[buffer(0)]],
                 device float *data_buffer[[buffer(1)]],
                  uint index[[thread_position_in_grid]])
{
  device float *input_data = data_buffer + INPUT_OFFSET;
  device float *output_data = data_buffer + OUTPUT_OFFSET;
    for (int gid = index; gid < N; gid += 4096) {
      float val = input_data[gid];
      if (val < 0.0) {
        val = 0.0;
      }
      output_data[gid] = val;
    }
}
      `;

      let kernel = new DNNPipelineKernel();
      kernel.kernelString = kernel_string;
      kernel.kernelFunctionName = 'relu';
      kernel.threadgroupsPerGrid = {
        width: 4096 / 512,
        height: 1,
        depth: 1
      };
      kernel.threadsPerThreadgroup = {
        width: 512,
        height: 1,
        depth: 1
      };

      return [kernel];
    }
  }
}
