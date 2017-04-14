/// <reference path="../../build/array_prototype/webdnn.d.ts" />
/// <reference path="../common/harness.ts" />


namespace SgemmTest {
    let webgpu: WebDNN.WebGPUHandler;
    let harness: WebDNN.Test.Harness;

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

    function createSgemmTest(N: number, M: number = N, K: number = N) {
        let A, B, C;
        const T = 1;
        const I = 1;

        return {
            name: `sgemm-${N}`,
            setup: () => {
                harness.clearText();
                harness.log(`sgemm-${N}`);

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
            summarize: (elapsedTime: WebDNN.Test.StatsValue, test: WebDNN.Test.Test) => ({
                'name': test.name,
                'M': M,
                'N': N,
                'K': K,
                'elapsed time [ms]': elapsedTime.mean.toFixed(2),
                'std [ms]': elapsedTime.std.toFixed(2),
                'FLOPS [G op/s]': (((M * N * K * T) / (elapsedTime.mean * 1e-3)) * 1e-9).toFixed(2)
            }),
            iterationCount: I
        }
    }

    export async function main() {
        document.querySelector('button').disabled = true;

        try {
            harness.clearAll();

            await harness.runPerformanceTest(createSgemmTest(64));
            await harness.runPerformanceTest(createSgemmTest(128));
            await harness.runPerformanceTest(createSgemmTest(256));
            await harness.runPerformanceTest(createSgemmTest(512));
            await harness.runPerformanceTest(createSgemmTest(513));
            await harness.runPerformanceTest(createSgemmTest(1024));
            await harness.runPerformanceTest(createSgemmTest(2048));

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
