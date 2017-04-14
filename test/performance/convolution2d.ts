/// <reference path="../../build/array_prototype/webdnn.d.ts" />
/// <reference path="../common/harness.ts" />


namespace Convolution2dTest {
    let webgpu: WebDNN.WebGPUHandler;
    let harness: WebDNN.Test.Harness;

    class Convolution2dDescriptor {
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

        constructor(h1: number, w1: number, c1: number, c2: number,
                    kh: number = 3, kw: number = 3, sh: number = 1, sw: number = 1, ph: number = 1, pw: number = 1, batchsize: number = 1) {
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

    export function sgemm(M: number, N: number, K: number, alpha: number, A: WebGPUBuffer, B: WebGPUBuffer, beta: number, C: WebGPUBuffer) {
        let MNKBuffer = webgpu.createBuffer(new Int32Array([M, N, K]));
        let abBuffer = webgpu.createBuffer(new Float32Array([alpha, beta]));
        let pipeline = webgpu.getPipelineStateByName('test.sgemm64');

        let commandBuffer = webgpu.createCommandBuffer();
        let commandEncoder = commandBuffer.createComputeCommandEncoder();

        commandEncoder.setComputePipelineState(pipeline);
        commandEncoder.setBuffer(MNKBuffer, 0, 0);
        commandEncoder.setBuffer(abBuffer, 0, 1);
        commandEncoder.setBuffer(A, 0, 2);
        commandEncoder.setBuffer(B, 0, 3);
        commandEncoder.setBuffer(C, 0, 4);
        commandEncoder.dispatch(
            {width: Math.ceil(M / 64), height: Math.ceil(N / 64), depth: 1},
            {width: 8, height: 8, depth: 1}
        );
        commandEncoder.endEncoding();
        commandBuffer.commit();
    }

    function convolution2dNaive(desc: Convolution2dDescriptor, X: WebGPUBuffer, W: WebGPUBuffer, Y: WebGPUBuffer) {
        let commandBuffer = webgpu.createCommandBuffer();
        let commandEncoder = commandBuffer.createComputeCommandEncoder();

        commandEncoder.setComputePipelineState(webgpu.getPipelineStateByName('test.convolution2d_naive'));
        commandEncoder.setBuffer(desc.buffer, 0, 0);
        commandEncoder.setBuffer(X, 0, 1);
        commandEncoder.setBuffer(W, 0, 2);
        commandEncoder.setBuffer(Y, 0, 3);
        commandEncoder.dispatch(
            {width: Math.ceil(desc.batchsize * desc.c2 * desc.h2 * desc.w2 / 512), height: 1, depth: 1},
            {width: 512, height: 1, depth: 1}
        );
        commandEncoder.endEncoding();
        commandBuffer.commit();
    }

    function convolution2dIm2col(desc: Convolution2dDescriptor, X: WebGPUBuffer, W: WebGPUBuffer, Y: WebGPUBuffer) {
        let col = webgpu.createBuffer(new Float32Array(desc.batchsize * desc.h2 * desc.w2 * desc.c1 * desc.kh * desc.kw));

        let commandBuffer = webgpu.createCommandBuffer();
        let commandEncoder = commandBuffer.createComputeCommandEncoder();

        commandEncoder.setComputePipelineState(webgpu.getPipelineStateByName('test.im2col'));
        commandEncoder.setBuffer(desc.buffer, 0, 0);
        commandEncoder.setBuffer(X, 0, 1);
        commandEncoder.setBuffer(col, 0, 2);
        commandEncoder.dispatch(
            {width: Math.ceil(desc.c1 * desc.kh * desc.kw * desc.batchsize * desc.h2 * desc.w2 / 1024), height: 1, depth: 1},
            {width: 1024, height: 1, depth: 1}
        );
        commandEncoder.endEncoding();
        commandBuffer.commit();

        sgemm(desc.batchsize * desc.h2 * desc.w2, desc.c2, desc.c1 * desc.kh * desc.kw, 1.0, col, W, 0.0, Y);
    }

    document.addEventListener('DOMContentLoaded', async () => {
        webgpu = new WebDNN.WebGPUHandler();
        await webgpu.init();

        harness = new WebDNN.Test.Harness(webgpu, document.getElementById("log"));

        await harness.fetchKernel((document.getElementById('sgemm') as HTMLScriptElement).src);
        await harness.fetchKernel((document.getElementById('convolution2d') as HTMLScriptElement).src);
    });


    function createConvolutionTest(H1: number, W1: number, C1: number, C2: number) {
        const T = 1;
        const I = 500;
        const K = 3;
        let desc: Convolution2dDescriptor;
        let X, W, Y;

        return {
            setup: () => {
                harness.clearText();
                harness.log(`${H1}, ${W1}, ${C1}, ${C2}`);

                desc = new Convolution2dDescriptor(H1, W1, C1, C2);

                X = new Float32Array(desc.batchsize * desc.h1 * desc.w1 * desc.c1);
                W = new Float32Array(desc.c1 * desc.kh * desc.kw * desc.c2);
                Y = new Float32Array(desc.batchsize * desc.h2 * desc.w2 * desc.c2);

                for (let i = 0; i < X.length; i++) X[i] = Math.random();
                for (let i = 0; i < W.length; i++) W[i] = Math.random();

                X = webgpu.createBuffer(X);
                W = webgpu.createBuffer(W);
                Y = webgpu.createBuffer(Y);
            },
            main: () => {
                for (let i = 0; i < T; i++) {
                    convolution2dIm2col(desc, X, W, Y);
                }
            },
            cleanup: () => {
                desc = null;
                X = null;
                W = null;
                Y = null;
            },
            summarize: (elapsedTime: WebDNN.Test.StatsValue, test: WebDNN.Test.Test) => ({
                'H1': H1,
                'W1': W1,
                'C1': C1,
                'C2': C2,
                'K': K,
                'Elapsed time [ms]': elapsedTime.mean.toFixed(2),
                'Std [ms]': elapsedTime.std.toFixed(2),
                'best': elapsedTime.min,
                'arg_best': elapsedTime.argmin,
                'worst': elapsedTime.max,
                'arg_worst': elapsedTime.argmax,
                'FLOPS [G op/s]': (((H1 * W1 * K * K * C1 * C2 * T) / (elapsedTime.mean * 1e-3)) * 1e-9).toFixed(2)
            }),
            iterationCount: I
        }
    }

    export async function main() {
        document.querySelector('button').disabled = true;

        try {
            harness.clearAll();

            await harness.runPerformanceTest(createConvolutionTest(56, 56, 64, 64));
            await harness.runPerformanceTest(createConvolutionTest(28, 28, 128, 128));
            await harness.runPerformanceTest(createConvolutionTest(14, 14, 256, 256));
            await harness.runPerformanceTest(createConvolutionTest(7, 7, 512, 512));

            harness.clearText();
            harness.show();

        } catch (e) {
            harness.error(e);
            console.error(e);
        }

        document.querySelector('button').disabled = false;
    }
}
