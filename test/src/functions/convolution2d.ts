/// <reference path="./prototype_kernel.ts" />
/// <reference path="./sgemm.ts" />

namespace WebDNN {
    export namespace PrototypeKernel {
        export type Convolution2dAlgo = 'naive' | 'im2col';

        export class Convolution2dDescriptor {
            algo: Convolution2dAlgo;
            kw: number;
            kh: number;
            sw: number;
            sh: number;
            pw: number;
            ph: number;
            batchsize: number;
            w1: number;
            h1: number;
            c1: number;
            c2: number;
            w2: number;
            h2: number;
            buffer: WebGPUBuffer;

            constructor(
                algo: Convolution2dAlgo, h1: number, w1: number, c1: number, c2: number,
                kh: number = 3, kw: number = 3, sh: number = 1, sw: number = 1, ph: number = 1, pw: number = 1, batchsize: number = 1
            ) {
                this.algo = algo;
                this.kw = kw;
                this.kh = kh;
                this.sw = sw;
                this.sh = sh;
                this.pw = pw;
                this.ph = ph;
                this.batchsize = batchsize;
                this.w1 = w1;
                this.h1 = h1;
                this.c1 = c1;
                this.c2 = c2;

                this.w2 = (this.w1 + 2 * this.pw - this.kw) / this.sw + 1;
                this.h2 = (this.h1 + 2 * this.ph - this.kh) / this.sh + 1;

                this.buffer = webgpu.createBuffer(new Int32Array([
                    this.kw, this.kh, this.sw, this.sh, this.pw, this.ph,
                    this.batchsize, this.w1, this.h1, this.c1, this.c2
                ]));
            }
        }

        export function convolution2d(desc: Convolution2dDescriptor, X: WebGPUBuffer, W: WebGPUBuffer, Y: WebGPUBuffer) {
            switch (desc.algo) {
                case 'naive':
                    return convolution2dNaive(desc, X, W, Y);

                case 'im2col':
                    return convolution2dIm2col(desc, X, W, Y);
            }
        }

        export function convolution2dNaive(desc: Convolution2dDescriptor, X: WebGPUBuffer, W: WebGPUBuffer, Y: WebGPUBuffer) {
            let commandBuffer = webgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(webgpu.getPipelineStateByName('prototype.convolution2d_naive'));
            commandEncoder.setBuffer(desc.buffer, 0, 0);
            commandEncoder.setBuffer(X, 0, 1);
            commandEncoder.setBuffer(W, 0, 2);
            commandEncoder.setBuffer(Y, 0, 3);
            commandEncoder.dispatch(
                { width: Math.ceil(desc.batchsize * desc.c2 * desc.h2 * desc.w2 / 512), height: 1, depth: 1 },
                { width: 512, height: 1, depth: 1 }
            );
            commandEncoder.endEncoding();
            commandBuffer.commit();
        }

        export function convolution2dIm2col(desc: Convolution2dDescriptor, X: WebGPUBuffer, W: WebGPUBuffer, Y: WebGPUBuffer) {
            let col = webgpu.createBuffer(new Float32Array(desc.batchsize * desc.h1 * desc.w1 * desc.c1 * desc.kh * desc.kw));

            let commandBuffer = webgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(webgpu.getPipelineStateByName('prototype.im2col'));
            commandEncoder.setBuffer(desc.buffer, 0, 0);
            commandEncoder.setBuffer(X, 0, 1);
            commandEncoder.setBuffer(col, 0, 2);
            commandEncoder.dispatch(
                { width: Math.ceil(desc.batchsize * desc.h1 * desc.w1 * desc.c1 / 1024), height: 1, depth: 1 },
                { width: 1024, height: 1, depth: 1 }
            );
            commandEncoder.endEncoding();
            commandBuffer.commit();

            sgemm(desc.batchsize * desc.h1 * desc.w1, desc.c2, desc.c1 * desc.kh * desc.kw, 1.0, col, W, 0.0, Y);
        }
    }
}
