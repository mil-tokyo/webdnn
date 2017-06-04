/// <reference path="./gpu_interface.ts" />
/// <reference path="../descriptor_runner/descriptor_runner_webassembly.ts" />

declare let WebAssembly;

namespace WebDNN {
    export class GPUInterfaceWebassembly extends GPUInterface<GraphDescriptorWebassembly, DescriptorRunnerWebassembly> {
        readonly backendName = 'webassembly';

        constructor(option?: any) {
            super();
            if (typeof Worker === 'undefined') {
                throw new Error('WebWorker is needed for WebAssembly backend');
            }
            if (typeof WebAssembly !== 'object') {
                console.warn('WebAssembly is not supported on this browser, trying to use asm.js code');
            }
        }

        async init() {
        }

        createDescriptorRunner() {
            return new DescriptorRunnerWebassembly();
        }
    }
}
