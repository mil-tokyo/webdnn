/// <reference path="./dnn_layer.ts" />

namespace WebDNN {
  export class ReluLayer extends DNNLayer {
    params: any;
    size: number;

    constructor(ioNames: DNNLayerIONames, params: any) {
      super(ioNames);
      this.params = params;
      this.size = <number>params.size;
      this.compile_kernel();
    }

    private compile_kernel(): void {
      DNN.webgpuHandler.loadKernel(`
#include <metal_stdlib>
using namespace metal;

kernel void relu(const device int *meta_int[[buffer(0)]],
                  const device float *meta_float[[buffer(1)]],
                  const device float *input_0[[buffer(2)]],
                  device float *output_0[[buffer(3)]],
                  uint index[[thread_position_in_grid]])
{
    const int n = meta_int[0];
    for (int gid = index; gid < n; gid += 4096) {
      float val = input_0[gid];
      if (val < 0.0) {
        val = 0.0;
      }
      output_0[gid] = val;
    }
}
      `, 'dnn');
    }

    getKernel(batchSize: number): DNNPrimitiveKernel {
      if (batchSize !== 1) {
        throw new Error();
      }

      let kernel = new DNNPrimitiveKernel();
      kernel.ioNames = this.ioNames;
      kernel.kernelFunctionName = 'dnn.relu';
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
      kernel.metaInts = [batchSize * this.size];
      kernel.metaFloats = [0.0];

      return kernel;
    }
    
  }
}
