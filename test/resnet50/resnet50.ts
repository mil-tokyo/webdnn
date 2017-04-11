/// <reference path="../src/test.ts" />
/// <reference path="../src/functions/sgemm.ts" />
/// <reference path="../src/functions/sync.ts" />

let webgpu: WebDNN.WebGPUHandler;
let runner: WebDNN.Test.Runner;
let logger: WebDNN.Test.DOMTextLogger;
let totalElapsedTime: number;

document.addEventListener('DOMContentLoaded', async () => {
    webgpu = new WebDNN.WebGPUHandler();
    await webgpu.init();

    runner = new WebDNN.Test.Runner(webgpu);
    logger = new WebDNN.Test.DOMTextLogger(runner, document.getElementById("log"));

    WebDNN.PrototypeKernel.init(webgpu);
    await WebDNN.PrototypeKernel.fetchKernel(document.getElementById('sgemm') as HTMLScriptElement);
    await WebDNN.PrototypeKernel.fetchKernel(document.getElementById('sync') as HTMLScriptElement);
});

function createSgemmTest(name: string, N: number, M: number = N, K: number = N) {
    let A, B, C;
    const T = 1;
    const I = 1;

    return {
        name: name,
        setup: () => {
            logger.clearText();
            logger.log(name);

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
        summarize: (elapsedTime: WebDNN.Test.StatsValue, test: WebDNN.Test.PerformanceTest) => {
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

async function main() {
    document.querySelector('button').disabled = true;

    try {
        totalElapsedTime = 0;
        logger.clearAll();

        //conv1
        await runner.runPerformanceTest(createSgemmTest('conv1', 112 * 112, 3 * 7 * 7, 64));

        //conv2.x
        await runner.runPerformanceTest(createSgemmTest('conv2.1.1', 56 * 56, 64 * 1 * 1, 64));
        await runner.runPerformanceTest(createSgemmTest('conv2.1.2', 56 * 56, 64 * 3 * 3, 64));
        await runner.runPerformanceTest(createSgemmTest('conv2.1.3', 56 * 56, 64 * 1 * 1, 256));

        await runner.runPerformanceTest(createSgemmTest('conv2.2.1', 56 * 56, 256 * 1 * 1, 64));
        await runner.runPerformanceTest(createSgemmTest('conv2.2.2', 56 * 56, 64 * 3 * 3, 64));
        await runner.runPerformanceTest(createSgemmTest('conv2.2.3', 56 * 56, 64 * 1 * 1, 256));

        await runner.runPerformanceTest(createSgemmTest('conv2.3.1', 56 * 56, 256 * 1 * 1, 64));
        await runner.runPerformanceTest(createSgemmTest('conv2.3.2', 56 * 56, 64 * 3 * 3, 64));
        await runner.runPerformanceTest(createSgemmTest('conv2.3.3', 56 * 56, 64 * 1 * 1, 256));

        //conv3.x
        await runner.runPerformanceTest(createSgemmTest('conv3.1.1', 28 * 28, 256 * 1 * 1, 128));
        await runner.runPerformanceTest(createSgemmTest('conv3.1.2', 28 * 28, 128 * 3 * 3, 128));
        await runner.runPerformanceTest(createSgemmTest('conv3.1.3', 28 * 28, 128 * 1 * 1, 512));

        await runner.runPerformanceTest(createSgemmTest('conv3.2.1', 28 * 28, 512 * 1 * 1, 128));
        await runner.runPerformanceTest(createSgemmTest('conv3.2.2', 28 * 28, 128 * 3 * 3, 128));
        await runner.runPerformanceTest(createSgemmTest('conv3.2.3', 28 * 28, 128 * 1 * 1, 512));

        await runner.runPerformanceTest(createSgemmTest('conv3.3.1', 28 * 28, 512 * 1 * 1, 128));
        await runner.runPerformanceTest(createSgemmTest('conv3.3.2', 28 * 28, 128 * 3 * 3, 128));
        await runner.runPerformanceTest(createSgemmTest('conv3.3.3', 28 * 28, 128 * 1 * 1, 512));

        await runner.runPerformanceTest(createSgemmTest('conv3.4.1', 28 * 28, 512 * 1 * 1, 128));
        await runner.runPerformanceTest(createSgemmTest('conv3.4.2', 28 * 28, 128 * 3 * 3, 128));
        await runner.runPerformanceTest(createSgemmTest('conv3.4.3', 28 * 28, 128 * 1 * 1, 512));

        //conv4.x
        await runner.runPerformanceTest(createSgemmTest('conv4.1.1', 14 * 14, 256 * 1 * 1, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.1.2', 14 * 14, 256 * 3 * 3, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.1.3', 14 * 14, 256 * 1 * 1, 1024));

        await runner.runPerformanceTest(createSgemmTest('conv4.2.1', 14 * 14, 1024 * 1 * 1, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.2.2', 14 * 14, 256 * 3 * 3, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.2.3', 14 * 14, 256 * 1 * 1, 1024));

        await runner.runPerformanceTest(createSgemmTest('conv4.3.1', 14 * 14, 1024 * 1 * 1, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.3.2', 14 * 14, 256 * 3 * 3, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.3.3', 14 * 14, 256 * 1 * 1, 1024));

        await runner.runPerformanceTest(createSgemmTest('conv4.4.1', 14 * 14, 1024 * 1 * 1, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.4.2', 14 * 14, 256 * 3 * 3, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.4.3', 14 * 14, 256 * 1 * 1, 1024));

        await runner.runPerformanceTest(createSgemmTest('conv4.5.1', 14 * 14, 1024 * 1 * 1, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.5.2', 14 * 14, 256 * 3 * 3, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.5.3', 14 * 14, 256 * 1 * 1, 1024));

        await runner.runPerformanceTest(createSgemmTest('conv4.6.1', 14 * 14, 1024 * 1 * 1, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.6.2', 14 * 14, 256 * 3 * 3, 256));
        await runner.runPerformanceTest(createSgemmTest('conv4.6.3', 14 * 14, 256 * 1 * 1, 1024));

        //conv5.x
        await runner.runPerformanceTest(createSgemmTest('conv5.1.1', 7 * 7, 1024 * 1 * 1, 512));
        await runner.runPerformanceTest(createSgemmTest('conv5.1.2', 7 * 7, 512 * 3 * 3, 512));
        await runner.runPerformanceTest(createSgemmTest('conv5.1.3', 7 * 7, 512 * 1 * 1, 2048));

        await runner.runPerformanceTest(createSgemmTest('conv5.2.1', 7 * 7, 2048 * 1 * 1, 512));
        await runner.runPerformanceTest(createSgemmTest('conv5.2.2', 7 * 7, 512 * 3 * 3, 512));
        await runner.runPerformanceTest(createSgemmTest('conv5.2.3', 7 * 7, 512 * 1 * 1, 2048));

        await runner.runPerformanceTest(createSgemmTest('conv5.3.1', 7 * 7, 2048 * 1 * 1, 512));
        await runner.runPerformanceTest(createSgemmTest('conv5.3.2', 7 * 7, 512 * 3 * 3, 512));
        await runner.runPerformanceTest(createSgemmTest('conv5.3.3', 7 * 7, 512 * 1 * 1, 2048));

        //fc
        await runner.runPerformanceTest(createSgemmTest('fc', 1, 2048, 1000));

        logger.clearText();
        logger.bold(`Total elapsed time: ${totalElapsedTime.toFixed(2)}[ms]`);
        logger.success('summary');
        logger.show();

    } catch (e) {
        logger.error(e);
        console.error(e);
    }

    document.querySelector('button').disabled = false;
}