/// <reference path="./dnn/dnn_descriptor_runner_webgpu.ts" />

declare var WebGPUComputeCommandEncoder;

namespace WebDNN {
    export class GPUInterfaceWebGPU implements GPUInterface {
        webgpuHandler: WebGPUHandler;
        shaderLanguage: string;

        constructor(private option?: any) {
            if (typeof WebGPUComputeCommandEncoder !== 'function') {
                throw new Error('WebGPU is not supported on this browser');
            }
        }

        async init() {
            // initialize webgpu, build kernels
            this.shaderLanguage = 'metal';
            this.webgpuHandler = new WebGPUHandler();
            await this.webgpuHandler.init();
            DNNBufferWebGPU.init(this.webgpuHandler);
            this.init_basic_kernels();
        }

        private init_basic_kernels() {
            this.webgpuHandler.loadKernel(`kernel void sync(){}`, 'basic');

        }

        createDNNDescriptorRunner(): DNNDescriptorRunner {
            return new DNNDescriptorRunnerWebGPU(this.webgpuHandler);
        }
    }
}
