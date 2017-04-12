/// <reference path="../src/test.ts" />
/// <reference path="../src/functions/convolution2d.ts" />
/// <reference path="../src/functions/sync.ts" />

namespace Convolution2dPerformanceTest {
    let webgpu: WebDNN.WebGPUHandler;
    let runner: WebDNN.Test.Runner;
    let logger: WebDNN.Test.DOMTextLogger;

    document.addEventListener('DOMContentLoaded', async () => {
        webgpu = new WebDNN.WebGPUHandler();
        await webgpu.init();

        runner = new WebDNN.Test.Runner(webgpu);
        logger = new WebDNN.Test.DOMTextLogger(runner, document.getElementById("log"));

        WebDNN.PrototypeKernel.init(webgpu);
        await WebDNN.PrototypeKernel.fetchKernel(document.getElementById('sgemm') as HTMLScriptElement);
        await WebDNN.PrototypeKernel.fetchKernel(document.getElementById('convolution2d') as HTMLScriptElement);
        await WebDNN.PrototypeKernel.fetchKernel(document.getElementById('sync') as HTMLScriptElement);
    });

    function createConvolutionTest(algo: WebDNN.PrototypeKernel.Convolution2dAlgo, H1: number, W1: number, C1: number, C2: number) {
        const T = 5;
        const I = 5;
        const K = 3;
        let desc: WebDNN.PrototypeKernel.Convolution2dDescriptor;
        let X, W, Y;

        return {
            setup: () => {
                logger.clearText();
                logger.log(`Algorithm: ${algo}`);

                desc = new WebDNN.PrototypeKernel.Convolution2dDescriptor(algo, H1, W1, C1, C2);

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
                    WebDNN.PrototypeKernel.convolution2d(desc, X, W, Y);
                }
            },
            cleanup: () => {
                desc = null;
                X = null;
                W = null;
                Y = null;
            },
            summarize: (elapsedTime: WebDNN.Test.StatsValue, test: WebDNN.Test.PerformanceTest) => ({
                'Algorithm': algo,
                'H1': H1,
                'W1': W1,
                'C1': C1,
                'C2': C2,
                'K': K,
                'Elapsed time [ms]': elapsedTime.mean.toFixed(2),
                'Std [ms]': elapsedTime.std.toFixed(2),
                'FLOPS [G op/s]': (((H1 * W1 * K * K * C1 * C2 * T) / (elapsedTime.mean * 1e-3)) * 1e-9).toFixed(2)
            }),
            iterationCount: I
        }
    }

    export async function main() {
        document.querySelector('button').disabled = true;

        try {
            logger.clearAll();
            await runner.runPerformanceTest(createConvolutionTest('naive', 56, 56, 64, 64));
            await runner.runPerformanceTest(createConvolutionTest('im2col', 56, 56, 64, 64));
            logger.clearText();
            logger.show();

            logger.clearSummary();
            await runner.runPerformanceTest(createConvolutionTest('naive', 28, 28, 128, 128));
            await runner.runPerformanceTest(createConvolutionTest('im2col', 28, 28, 128, 128));
            logger.clearText();
            logger.show();

            logger.clearSummary();
            await runner.runPerformanceTest(createConvolutionTest('naive', 14, 14, 256, 256));
            await runner.runPerformanceTest(createConvolutionTest('im2col', 14, 14, 256, 256));
            logger.clearText();
            logger.show();

            logger.clearSummary();
            await runner.runPerformanceTest(createConvolutionTest('naive', 7, 7, 512, 512));
            await runner.runPerformanceTest(createConvolutionTest('im2col', 7, 7, 512, 512));
            logger.clearText();
            logger.show();

        } catch (e) {
            logger.error(e);
            console.error(e);
        }

        document.querySelector('button').disabled = false;
    }
}