/// <reference path="./dnn/dnn_descriptor_runner_fallback.ts" />

namespace WebDNN {
    export class GPUInterfaceFallback implements GPUInterface {
        constructor(private option?: any) {

        }

        async init(option?: any) {
        }

        createDNNDescriptorRunner(): DNNDescriptorRunner {
            return new DNNDescriptorRunnerFallback();
        }
    }
}
