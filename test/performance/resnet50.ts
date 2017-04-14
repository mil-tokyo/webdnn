/// <reference path="../../build/array_prototype/webdnn.d.ts" />
/// <reference path="../common/harness.ts" />


namespace ResNet50Test {
    let webgpu: WebDNN.WebGPUHandler;
    let harness: WebDNN.Test.Harness;
    let totalElapsedTime: number;

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

    document.addEventListener('DOMContentLoaded', async () => {
        webgpu = new WebDNN.WebGPUHandler();
        await webgpu.init();

        harness = new WebDNN.Test.Harness(webgpu, document.getElementById("log"));

        await harness.fetchKernel((document.getElementById('sgemm') as HTMLScriptElement).src);
    });

    function createSgemmTest(name: string, N: number, M: number = N, K: number = N) {
        let A, B, C;
        const T = 1;
        const I = 1;

        return {
            name: name,
            setup: () => {
                harness.clearText();
                harness.log(name);

                A = new Float32Array(M * K);
                B = new Float32Array(K * N);
                C = new Float32Array(M * N);

                for (let i = 0; i < A.length; i++) A[i] = Math.random();
                for (let i = 0; i < B.length; i++) B[i] = Math.random();
                for (let i = 0; i < C.length; i++) C[i] = Math.random();

                A = webgpu.createBuffer(A);
                B = webgpu.createBuffer(B);
                C = webgpu.createBuffer(C);
            },
            main: () => {
                for (let i = 0; i < T; i++) {
                    sgemm(M, N, K, 1.0, A, B, 0.0, C);
                }
            },
            cleanup: () => {
                A = null;
                B = null;
                C = null;
            },
            summarize: (elapsedTime: WebDNN.Test.StatsValue, test: WebDNN.Test.Test) => {
                totalElapsedTime += elapsedTime.mean;

                return {
                    'name': test.name,
                    'M': M,
                    'N': N,
                    'K': K,
                    'elapsed time [ms]': elapsedTime.mean.toFixed(2),
                    'std [ms]': elapsedTime.std.toFixed(2),
                    'FLOPS [G op/s]': (((M * N * K * T) / (elapsedTime.mean * 1e-3)) * 1e-9).toFixed(2)
                }
            },
            iterationCount: I
        }
    }

    export async function main() {
        document.querySelector('button').disabled = true;

        try {
            totalElapsedTime = 0;
            harness.clearAll();

            //conv1
            await harness.runPerformanceTest(createSgemmTest('conv1', 112 * 112, 3 * 7 * 7, 64));

            //conv2.x
            await harness.runPerformanceTest(createSgemmTest('conv2.1.1', 56 * 56, 64, 64));
            await harness.runPerformanceTest(createSgemmTest('conv2.1.2', 56 * 56, 64 * 3 * 3, 64));
            await harness.runPerformanceTest(createSgemmTest('conv2.1.3', 56 * 56, 64, 256));

            await harness.runPerformanceTest(createSgemmTest('conv2.2.1', 56 * 56, 256, 64));
            await harness.runPerformanceTest(createSgemmTest('conv2.2.2', 56 * 56, 64 * 3 * 3, 64));
            await harness.runPerformanceTest(createSgemmTest('conv2.2.3', 56 * 56, 64, 256));

            await harness.runPerformanceTest(createSgemmTest('conv2.3.1', 56 * 56, 256, 64));
            await harness.runPerformanceTest(createSgemmTest('conv2.3.2', 56 * 56, 64 * 3 * 3, 64));
            await harness.runPerformanceTest(createSgemmTest('conv2.3.3', 56 * 56, 64, 256));

            //conv3.x
            await harness.runPerformanceTest(createSgemmTest('conv3.1.1', 28 * 28, 256, 128));
            await harness.runPerformanceTest(createSgemmTest('conv3.1.2', 28 * 28, 128 * 3 * 3, 128));
            await harness.runPerformanceTest(createSgemmTest('conv3.1.3', 28 * 28, 128, 512));

            await harness.runPerformanceTest(createSgemmTest('conv3.2.1', 28 * 28, 512, 128));
            await harness.runPerformanceTest(createSgemmTest('conv3.2.2', 28 * 28, 128 * 3 * 3, 128));
            await harness.runPerformanceTest(createSgemmTest('conv3.2.3', 28 * 28, 128, 512));

            await harness.runPerformanceTest(createSgemmTest('conv3.3.1', 28 * 28, 512, 128));
            await harness.runPerformanceTest(createSgemmTest('conv3.3.2', 28 * 28, 128 * 3 * 3, 128));
            await harness.runPerformanceTest(createSgemmTest('conv3.3.3', 28 * 28, 128, 512));

            await harness.runPerformanceTest(createSgemmTest('conv3.4.1', 28 * 28, 512, 128));
            await harness.runPerformanceTest(createSgemmTest('conv3.4.2', 28 * 28, 128 * 3 * 3, 128));
            await harness.runPerformanceTest(createSgemmTest('conv3.4.3', 28 * 28, 128, 512));

            //conv4.x
            await harness.runPerformanceTest(createSgemmTest('conv4.1.1', 14 * 14, 256, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.1.2', 14 * 14, 256 * 3 * 3, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.1.3', 14 * 14, 256, 1024));

            await harness.runPerformanceTest(createSgemmTest('conv4.2.1', 14 * 14, 1024, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.2.2', 14 * 14, 256 * 3 * 3, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.2.3', 14 * 14, 256, 1024));

            await harness.runPerformanceTest(createSgemmTest('conv4.3.1', 14 * 14, 1024, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.3.2', 14 * 14, 256 * 3 * 3, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.3.3', 14 * 14, 256, 1024));

            await harness.runPerformanceTest(createSgemmTest('conv4.4.1', 14 * 14, 1024, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.4.2', 14 * 14, 256 * 3 * 3, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.4.3', 14 * 14, 256, 1024));

            await harness.runPerformanceTest(createSgemmTest('conv4.5.1', 14 * 14, 1024, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.5.2', 14 * 14, 256 * 3 * 3, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.5.3', 14 * 14, 256, 1024));

            await harness.runPerformanceTest(createSgemmTest('conv4.6.1', 14 * 14, 1024, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.6.2', 14 * 14, 256 * 3 * 3, 256));
            await harness.runPerformanceTest(createSgemmTest('conv4.6.3', 14 * 14, 256, 1024));

            //conv5.x
            await harness.runPerformanceTest(createSgemmTest('conv5.1.1', 7 * 7, 1024, 512));
            await harness.runPerformanceTest(createSgemmTest('conv5.1.2', 7 * 7, 512 * 3 * 3, 512));
            await harness.runPerformanceTest(createSgemmTest('conv5.1.3', 7 * 7, 512, 2048));

            await harness.runPerformanceTest(createSgemmTest('conv5.2.1', 7 * 7, 2048, 512));
            await harness.runPerformanceTest(createSgemmTest('conv5.2.2', 7 * 7, 512 * 3 * 3, 512));
            await harness.runPerformanceTest(createSgemmTest('conv5.2.3', 7 * 7, 512, 2048));

            await harness.runPerformanceTest(createSgemmTest('conv5.3.1', 7 * 7, 2048, 512));
            await harness.runPerformanceTest(createSgemmTest('conv5.3.2', 7 * 7, 512 * 3 * 3, 512));
            await harness.runPerformanceTest(createSgemmTest('conv5.3.3', 7 * 7, 512, 2048));

            //fc
            await harness.runPerformanceTest(createSgemmTest('fc', 1, 2048, 1000));

            harness.clearText();
            harness.bold(`Total elapsed time: ${totalElapsedTime.toFixed(2)}[ms]`);
            harness.success('summary');
            harness.show();

            harness.clearText();
            harness.success('summary');
            harness.show();

        } catch (e) {
            harness.error(e);
            console.error(e);
        }

        document.querySelector('button').disabled = false;
    }
}
