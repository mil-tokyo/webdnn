/// <reference path="./gpu_interface.ts" />
/// <reference path="./dnn/dnn_descriptor_runner_webassembly.ts" />

namespace WebDNN {
    export class GPUInterfaceWebassembly implements GPUInterface {

        constructor(private option?: any) {

        }

        async init() {
        }


        createDNNDescriptorRunner(dnnDescriptor: any): DNNDescriptorRunner {
            return new DNNDescriptorRunnerWebassembly(dnnDescriptor);
        }
    }
}
