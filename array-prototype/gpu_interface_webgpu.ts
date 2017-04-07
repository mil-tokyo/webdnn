namespace WebDNN {
  export class GPUInterfaceWebGPU implements GPUInterface {
    webgpuHandler: WebGPUHandler;

    async init(option?: any) {
      // initialize webgpu, build kernels
      this.webgpuHandler = new WebGPUHandler();
      await this.webgpuHandler.init();
      MatrixWebGPU.init(this.webgpuHandler);
      this.init_basic_kernels();
    }

    private init_basic_kernels() {
      this.webgpuHandler.loadKernel(`
kernel void sync(){}
      `, 'basic');

      [['add', '+'], ['sub', '-'], ['mul', '*'], ['div', '/']].forEach((op) => {
        this.webgpuHandler.loadKernel(`
#include <metal_stdlib>
using namespace metal;

kernel void ${op[0]}(const device int *_n[[buffer(0)]],
                  const device float *a[[buffer(1)]],
                  const device float *b[[buffer(2)]],
                  device float *c[[buffer(3)]],
                  uint index[[thread_position_in_grid]])
{
    const int n = _n[0];
    for (int gid = index; gid < n; gid += 4096)
        c[gid] = a[gid] ${op[1]} b[gid];
}
      `, 'basic');
      });

    }

    toGPU(m: MatrixCPU): MatrixGPU {
      return new MatrixWebGPU(m.shape, m.data);
    }

    async toCPU(m: MatrixWebGPU): Promise<MatrixCPU> {
      await this.webgpuHandler.sync();
      if (m.size > 0) {
        // copy data here so as not to modify GPU data
        return new MatrixCPU(m.shape, m.webgpuBufferView.slice(), true);
      } else {
        // synchronize even if 0 byte matrix is used
        return new MatrixCPU(m.shape);
      }
    }


    add(a: MatrixWebGPU, b: MatrixWebGPU): MatrixWebGPU {
      return this.add_sub_mul_div('add', a, b);
    }
    sub(a: MatrixWebGPU, b: MatrixWebGPU): MatrixWebGPU {
      return this.add_sub_mul_div('sub', a, b);
    }
    mul(a: MatrixWebGPU, b: MatrixWebGPU): MatrixWebGPU {
      return this.add_sub_mul_div('mul', a, b);
    }
    div(a: MatrixWebGPU, b: MatrixWebGPU): MatrixWebGPU {
      return this.add_sub_mul_div('div', a, b);
    }

    private add_sub_mul_div(op: string, a: MatrixWebGPU, b: MatrixWebGPU): MatrixWebGPU {
      let c = new MatrixWebGPU(a.shape);
      let nbuffer = this.webgpuHandler.createBuffer(new Int32Array([a.size]));
      this.webgpuHandler.executeSinglePipelineState('basic.' + op, {
        width: 4096 / 512,
        height: 1,
        depth: 1
      }, {
          width: 512,
          height: 1,
          depth: 1
        }, [nbuffer, a, b, c]);

      return c;
    }
  }
}
