/// <reference path="./dnn_layer.ts" />

namespace WebDNN {
  export class FullyConnectedLayer extends DNNLayer {
    params: any;
    inDim: number;
    outDim: number;

    constructor(ioNames: DNNLayerIONames, params: any) {
      super(ioNames);
      this.params = params;
      this.inDim = <number>params.inDim;
      this.outDim = <number>params.outDim;
      this.compile_kernel();
    }

    private compile_kernel(): void {
      // weight: [in_ch, out_ch]
      DNN.webgpuHandler.loadKernel(`
#include <metal_stdlib>
using namespace metal;

kernel void fully_connected_mul(const device int *meta_int[[buffer(0)]],
                  const device float *meta_float[[buffer(1)]],
                  const device float *input_0[[buffer(2)]],
                  device float *output_0[[buffer(3)]],
                  const device float *weight_0[[buffer(4)]],
                  uint index[[thread_position_in_grid]])
{
    const int n = meta_int[0];
    const int in_ch = meta_int[1];
    const int out_ch = meta_int[2];
    for (int gid = index; gid < n; gid += 4096) {
      int out_chid = gid % out_ch;
      int sample_id = gid / out_ch;
      float sum = 0.0;
      for (int in_chid = 0; in_chid < in_ch; in_chid++) {
        sum += input_0[sample_id * in_ch + in_chid] * weight_0[in_chid * out_ch + out_chid];
      }
      output_0[gid] = sum;
    }
}

kernel void fully_connected_bias(const device int *meta_int[[buffer(0)]],
                  const device float *meta_float[[buffer(1)]],
                  const device float *input_0[[buffer(2)]],
                  device float *output_0[[buffer(3)]],
                  const device float *weight_0[[buffer(4)]],
                  uint index[[thread_position_in_grid]])
{
    const int n = meta_int[0];
    const int ch = meta_int[1];
    for (int gid = index; gid < n; gid += 4096) {
      int chid = gid % ch;
      output_0[gid] = input_0[gid] + weight_0[chid];
    }
}
      `, 'dnn');
    }

    getKernel(batchSize: number): DNNPrimitiveKernel[] {
      if (batchSize !== 1) {
        throw new Error();
      }

      let kernel_weight = new DNNPrimitiveKernel();
      kernel_weight.ioNames = new DNNLayerIONames(this.ioNames.inputs, this.ioNames.outputs, [this.ioNames.weights[0]]);
      kernel_weight.kernelFunctionName = 'dnn.fully_connected_mul';
      kernel_weight.threadgroupsPerGrid = {
        width: 4096 / 512,
        height: 1,
        depth: 1
      };
      kernel_weight.threadsPerThreadgroup = {
        width: 512,
        height: 1,
        depth: 1
      };
      kernel_weight.metaInts = [batchSize * this.outDim, this.inDim, this.outDim];
      kernel_weight.metaFloats = [0.0];

      let kernel_bias = new DNNPrimitiveKernel();
      kernel_bias.ioNames = new DNNLayerIONames(this.ioNames.outputs, this.ioNames.outputs, [this.ioNames.weights[1]]);//in-place
      kernel_bias.kernelFunctionName = 'dnn.fully_connected_bias';
      kernel_bias.threadgroupsPerGrid = {
        width: 4096 / 512,
        height: 1,
        depth: 1
      };
      kernel_bias.threadsPerThreadgroup = {
        width: 512,
        height: 1,
        depth: 1
      };
      kernel_bias.metaInts = [batchSize * this.outDim, this.outDim];
      kernel_bias.metaFloats = [0.0];

      return [kernel_weight, kernel_bias];
    }
    
  }
}
