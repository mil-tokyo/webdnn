/// <reference path="./gpu_interface.ts" />
/// <reference path="./dnn/dnn_descriptor_runner_webassembly.ts" />

declare var WebAssembly;

namespace WebDNN {
    export class GPUInterfaceWebassembly implements GPUInterface {

        constructor(private option?: any) {
            if (typeof WebAssembly !== 'object') {
                throw new Error('WebAssembly is not supported on this browser');
            }
        }

        async init() {
        }


        createDNNDescriptorRunner(dnnDescriptor: any): DNNDescriptorRunner {
            return new DNNDescriptorRunnerWebassembly(dnnDescriptor);
        }
    }
}
