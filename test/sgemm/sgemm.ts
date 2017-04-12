/// <reference path="../src/test.ts" />
/// <reference path="../src/functions/sgemm.ts" />
/// <reference path="../src/functions/sync.ts" />

namespace SgemmPerformanceTest {
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
        await WebDNN.PrototypeKernel.fetchKernel(document.getElementById('sync') as HTMLScriptElement);
    });

    function createSgemmTest(N: number, M: number = N, K: number = N) {
        let A, B, C;
        const T = 7;
        const I = 30;

        return {
            name: `sgemm-${N}`,
            setup: () => {
                logger.clearText();
                logger.log(`sgemm-${N}`);

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
                    WebDNN.PrototypeKernel.sgemm(M, N, K, 1.0, A, B, 0.0, C);
                }
            },
            cleanup: () => {
                A = null;
                B = null;
                C = null;
            },
            summarize: (elapsedTime: WebDNN.Test.StatsValue, test: WebDNN.Test.PerformanceTest) => ({
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
            logger.clearAll();

            await runner.runPerformanceTest(createSgemmTest(64));
            await runner.runPerformanceTest(createSgemmTest(128));
            await runner.runPerformanceTest(createSgemmTest(256));
            await runner.runPerformanceTest(createSgemmTest(512));
            await runner.runPerformanceTest(createSgemmTest(513));
            await runner.runPerformanceTest(createSgemmTest(1024));
            await runner.runPerformanceTest(createSgemmTest(2048));

            logger.clearText();
            logger.success('summary');
            logger.show();

        } catch (e) {
            logger.error(e);
            console.error(e);
        }

        document.querySelector('button').disabled = false;
    }
}