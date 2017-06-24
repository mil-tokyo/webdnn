///<reference path="./descriptor_runner/descriptor_runner.ts" />
///<reference path="./descriptor_runner/descriptor_runner_webgpu.ts" />
///<reference path="./descriptor_runner/descriptor_runner_webassembly.ts" />
///<reference path="./descriptor_runner/descriptor_runner_fallback.ts" />

namespace WebDNN {
    export const backends = {
        'webgpu': DescriptorRunnerWebGPU,
        'webassembly': DescriptorRunnerWebassembly,
        'fallback': DescriptorRunnerFallback,
    };

    export let DEBUG: boolean = false;

    async function initBackend(backendName: string, option?: any): Promise<DescriptorRunner<GraphDescriptor> | null> {
        if (!(backendName in backends)) throw new Error(`Unknown backend: "${backendName}"`);

        let runner: DescriptorRunner<GraphDescriptor>;

        try {
            runner = new backends[backendName](option);
            await runner.init();
        } catch (ex) {
            console.warn(`Failed to initialize ${backendName} backend: ${ex}`);
            return null;
        }

        return runner;
    }

    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param backendOrder The trying order of backend names to be initialized.
     * @param backendOptions Backend options.
     * @param progressCallback callback which is called to notice the loading is progressing.
     */
    export interface InitOption {
        backendOrder?: string | string[],
        backendOptions?: { [key: string]: any },
        ignoreCache?: boolean,
        progressCallback?: (loaded: number, total: number) => any
    }

    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param directory URL of directory that contains graph descriptor files (e.g. graph_fallback.json)
     * @param initOption Initialize option
     * @return Interface to input/output data and run the model.
     */
    export async function load(directory: string, initOption: InitOption = {}): Promise<DescriptorRunner<GraphDescriptor>> {
        let backendOrder = initOption.backendOrder;
        if (!backendOrder) {
            backendOrder = ['webgpu', 'webassembly'];
        } else if (typeof backendOrder === 'string') {
            backendOrder = [backendOrder];
        }
        backendOrder = backendOrder.slice();
        if (backendOrder.indexOf('fallback') === -1) backendOrder.concat(['fallback']);

        let backendOptions = initOption.backendOptions || {};

        while (backendOrder.length > 0) {
            let backendName = backendOrder.shift()!;
            let runner: DescriptorRunner<GraphDescriptor> | null = await initBackend(backendName, backendOptions[backendName]);
            if (!runner) continue;
            runner.ignoreCache = Boolean(initOption.ignoreCache);

            try {
                await runner.load(directory, initOption.progressCallback);
            } catch (ex) {
                console.warn(`Model loading failed for ${backendName} backend. Trying next backend: ${ex.message}`);
            }

            return runner;
        }

        throw new Error('No backend is available');
    }
}
