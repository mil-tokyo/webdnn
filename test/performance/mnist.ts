/// <reference path="../../build/array_prototype/webdnn.d.ts" />
/// <reference path="../common/harness.ts" />


namespace MNISTTest {
    interface Sample {
        x: Float32Array,
        y: number
    }

    let harness: WebDNN.Test.Harness;

    document.addEventListener('DOMContentLoaded', async () => {
        await WebDNN.init();
        harness = new WebDNN.Test.Harness((WebDNN.gpu as WebDNN.GPUInterfaceWebGPU).webgpuHandler, document.getElementById("log"));
    });

    function createTest(flagRun: boolean) {
        let runner: WebDNN.DNNDescriptorRunner;
        let samples: Sample[];
        let inputView: Float32Array;
        let outputView: Float32Array;
        let numCorrect = -1;

        return {
            name: 'MNIST',
            setupAsync: async () => {
                harness.clearText();
                harness.log('test');

                // initialize graph
                let pipelineData = await(await fetch('../../example/mnist/output/graph.json')).json();
                runner = WebDNN.gpu.createDNNDescriptorRunner(pipelineData);
                await runner.compile();
                await runner.loadWeights(new Float32Array(await (await fetch('../../example/mnist/output/weight.bin')).arrayBuffer()));
                inputView = (await runner.getInputViews())[0];
                outputView = (await runner.getOutputViews())[0];

                // load samples
                samples = (await (await fetch('../../resources/mnist/test_samples.json')).json())
                    .map(sample => ({
                        x: new Float32Array(sample['x']['data']),
                        y: sample['y']
                    }));
            },
            mainAsync: async () => {
                numCorrect = 0;

                for (let sample of samples) {
                    let predictedLabel = 0;
                    let maxScore = 0;

                    inputView.set(sample.x);
                    flagRun && await runner.run();

                    for (let j = 0; j < outputView.length; j++) {
                        if (outputView[j] <= maxScore) continue;

                        maxScore = outputView[j];
                        predictedLabel = j;
                    }

                    if (predictedLabel === sample.y) numCorrect++;
                }
            },
            cleanup: () => {
                runner = null;
                inputView = null;
                samples = null;
            },
            summarize: (elapsedTime: WebDNN.Test.StatsValue, test: WebDNN.Test.Test) => {
                return {
                    'Name': test.name,
                    'Run?': flagRun,
                    'Accuracy': (numCorrect / samples.length).toFixed(3),
                    'Elapsed time [ms/image]': (elapsedTime.mean / samples.length).toFixed(2),
                    'Std [ms/image]': (elapsedTime.std / samples.length).toFixed(2)
                }
            }
        }
    }

    export async function main() {
        document.querySelector('button').disabled = true;

        try {
            harness.clearAll();

            await harness.runPerformanceTest(createTest(true));
            await harness.runPerformanceTest(createTest(false));

            harness.clearText();
            harness.show();

        } catch (e) {
            harness.error(e);
            console.error(e);
        }

        document.querySelector('button').disabled = false;
    }
}
