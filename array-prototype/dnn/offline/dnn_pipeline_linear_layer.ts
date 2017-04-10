namespace WebDNN {
  export class DNNPipelineLinearLayer implements DNNPipelineLayer {
    params: { in_size: number, out_size: number, nobias: boolean };
    constructor(params: any) {
      this.params = params;

      // bottom[0] -> mul(w[0]) -> temp[0] -> bias(w[1]) -> top[0]
      // bottom[0] -> mul(w[0]) -> top[0]
    }

    getKernels(ioBuffer: DNNPipelineLayerIOBuffer): DNNPipelineKernel[] {
      let kernels: DNNPipelineKernel[] = [];
      if (this.params.nobias) {
        kernels.push(this.makeKernelMul(ioBuffer.bottoms[0], ioBuffer.tops[0], ioBuffer.weights[0]));
      } else {
        kernels.push(this.makeKernelMul(ioBuffer.bottoms[0], ioBuffer.temporaries[0], ioBuffer.weights[0]));
        kernels.push(this.makeKernelBias(ioBuffer.temporaries[0], ioBuffer.tops[0], ioBuffer.weights[1]));
      }

      return kernels;
    }

    makeKernelMul(dataIn: DNNPipelineBuffer, dataOut: DNNPipelineBuffer, weight: DNNPipelineBuffer): DNNPipelineKernel {
      let kernel_string = `
#include <metal_stdlib>
using namespace metal;

#define WEIGHT_OFFSET ${weight.offset}
#define INPUT_OFFSET ${dataIn.offset}
#define OUTPUT_OFFSET ${dataOut.offset}
#define N ${dataOut.size}
#define IN_CH ${this.params.in_size}
#define OUT_CH ${this.params.out_size}

kernel void linear_mul(const device float *weight_buffer[[buffer(0)]],
                 device float *data_buffer[[buffer(1)]],
                  uint index[[thread_position_in_grid]])
{
  device float *input_data = data_buffer + INPUT_OFFSET;
  device float *output_data = data_buffer + OUTPUT_OFFSET;
  const device float *weight_data = weight_buffer + WEIGHT_OFFSET;
    for (int gid = index; gid < N; gid += 4096) {
      int out_chid = gid % OUT_CH;
      int sample_id = gid / OUT_CH;
      float sum = 0.0;
      for (int in_chid = 0; in_chid < IN_CH; in_chid++) {
        sum += input_data[sample_id * IN_CH + in_chid] * weight_data[in_chid * OUT_CH + out_chid];
      }
      output_data[gid] = sum;
    }
}
      `;

      let kernel = new DNNPipelineKernel();
      kernel.kernelString = kernel_string;
      kernel.kernelFunctionName = 'linear_mul';
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

      return kernel;
    }

    makeKernelBias(dataIn: DNNPipelineBuffer, dataOut: DNNPipelineBuffer, weight: DNNPipelineBuffer): DNNPipelineKernel {
      let kernel_string = `
#include <metal_stdlib>
using namespace metal;

#define BIAS_OFFSET ${weight.offset}
#define INPUT_OFFSET ${dataIn.offset}
#define OUTPUT_OFFSET ${dataOut.offset}
#define N ${dataOut.size}
#define IN_CH ${this.params.in_size}
#define OUT_CH ${this.params.out_size}

kernel void linear_bias(const device float *weight_buffer[[buffer(0)]],
                 device float *data_buffer[[buffer(1)]],
                  uint index[[thread_position_in_grid]])
{
  device float *input_data = data_buffer + INPUT_OFFSET;
  device float *output_data = data_buffer + OUTPUT_OFFSET;
  const device float *bias_data = weight_buffer + BIAS_OFFSET;
    for (int gid = index; gid < N; gid += 4096) {
      int chid = gid % OUT_CH;
      output_data[gid] = input_data[gid] + bias_data[chid];
    }
}
      `;

      let kernel = new DNNPipelineKernel();
      kernel.kernelString = kernel_string;
      kernel.kernelFunctionName = 'linear_bias';
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

      return kernel;
    }
  }
}
