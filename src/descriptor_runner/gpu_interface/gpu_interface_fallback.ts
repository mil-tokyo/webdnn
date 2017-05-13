/// <reference path="../descriptor_runner/descriptor_runner_fallback.ts" />

namespace WebDNN {
    export class GPUInterfaceFallback implements GPUInterface {
        constructor(private option?: any) {

        }

        async init(option?: any) {
        }

        createDescriptorRunner(): DescriptorRunner {
            return new DescriptorRunnerFallback();
        }
    }
}
