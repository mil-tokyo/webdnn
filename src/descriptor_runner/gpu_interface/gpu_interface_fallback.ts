/// <reference path="../descriptor_runner/descriptor_runner_fallback.ts" />

namespace WebDNN {
    export class GPUInterfaceFallback extends GPUInterface<GraphDescriptorFallback, DescriptorRunnerFallback> {
        readonly backendName = 'fallback';

        async init(option?: any) {
        }

        createDescriptorRunner() {
            return new DescriptorRunnerFallback();
        }
    }
}
