/// <reference path="./dnn/dnn_descriptor_runner_fallback.ts" />

namespace WebDNN {
    export class GPUInterfaceFallback implements GPUInterface {
        constructor(private option?: any) {

        }

        async init(option?: any) {
        }

        createDNNDescriptorRunner(dnnDescriptor: any): DNNDescriptorRunner {
            return new DNNDescriptorRunnerFallback(dnnDescriptor);
        }
    }
}
