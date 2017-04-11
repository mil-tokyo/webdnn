/// <reference path="./prototype_kernel.ts" />

namespace WebDNN {
    export namespace PrototypeKernel {
        export function sync() {
            let commandBuffer = webgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(webgpu.getPipelineStateByName('prototype.sync'));
            commandEncoder.dispatch(
                { width: 1, height: 1, depth: 1 },
                { width: 1, height: 1, depth: 1 }
            );
            commandEncoder.endEncoding();
            let promise = commandBuffer.completed;
            commandBuffer.commit();

            return promise;
        }
    }
}
