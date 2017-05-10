/// <reference path="./gpu_interface.ts" />
/// <reference path="./dnn/dnn_descriptor_runner_webassembly.ts" />

declare var WebAssembly;

namespace WebDNN {
    export class GPUInterfaceWebassembly implements GPUInterface {

        constructor(private option?: any) {
            if (typeof Worker === 'undefined') {
                throw new Error('WebWorker is needed for WebAssembly backend');
            }
            if (typeof WebAssembly !== 'object') {
                console.warn('WebAssembly is not supported on this browser, trying to use asm.js code');
            }
        }

        async init() {
        }


        createDNNDescriptorRunner(): DNNDescriptorRunner {
            return new DNNDescriptorRunnerWebassembly();
        }
    }
}
