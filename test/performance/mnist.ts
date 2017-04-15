/// <reference path="../../build/array_prototype/webdnn.d.ts" />
/// <reference path="../common/harness.ts" />


namespace MNISTTest {
    interface Sample {
        x: any,
        y: any
    }

    let harness: WebDNN.Test.Harness;

    document.addEventListener('DOMContentLoaded', async () => {
        await WebDNN.init();
        harness = new WebDNN.Test.Harness((WebDNN.gpu as WebDNN.GPUInterfaceWebGPU).webgpuHandler, document.getElementById("log"));
    });

    function createTest() {
        let runner: WebDNN.DNNDescriptorRunner;
        let samples: Sample[];
        let inputView: Float32Array[];

        return {
            name: 'test',
            setupAsync: async () => {
                harness.clearText();
                harness.log('test');

                // initialize graph
                let pipelineData = await(await fetch('../../example/mnist/output/graph.json')).json();
                runner = WebDNN.gpu.createDNNDescriptorRunner(pipelineData);
                await runner.compile();
                await runner.loadWeights(new Float32Array(await (await fetch('../../example/mnist/output/weight.bin')).arrayBuffer()));
                inputView = await runner.getInputViews();

                // load samples
                samples = (await (await fetch('../../resources/mnist/test_samples.json')).json())
                    .map(sample => ({
                        x: new Float32Array(sample['x']['data']),
                        y: sample['y']
                    }));
            },
            mainAsync: async () => {
                for (let sample of samples) {
                    inputView[0].set(sample.x);
                    await runner.run();
                }
            },
            cleanup: () => {
                runner = null;
                inputView = null;
                samples = null;
            },
            summarize: (elapsedTime: WebDNN.Test.StatsValue, test: WebDNN.Test.Test) => {
                return {
                    'name': test.name,
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

            await harness.runPerformanceTest(createTest());

            harness.clearText();
            harness.show();

        } catch (e) {
            harness.error(e);
            console.error(e);
        }

        document.querySelector('button').disabled = false;
    }
}
