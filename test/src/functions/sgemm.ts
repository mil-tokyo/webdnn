/// <reference path="./prototype_kernel.ts" />

namespace WebDNN {
    export namespace PrototypeKernel {
        export function sgemm(M: number, N: number, K: number, alpha: number, A: WebGPUBuffer, B: WebGPUBuffer, beta: number, C: WebGPUBuffer) {
            let MNKBuffer = webgpu.createBuffer(new Int32Array([M, N, K]));
            let abBuffer = webgpu.createBuffer(new Float32Array([alpha, beta]));

            let commandBuffer = webgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(webgpu.getPipelineStateByName('prototype.sgemm64'));
            commandEncoder.setBuffer(MNKBuffer, 0, 0);
            commandEncoder.setBuffer(abBuffer, 0, 1);
            commandEncoder.setBuffer(A, 0, 2);
            commandEncoder.setBuffer(B, 0, 3);
            commandEncoder.setBuffer(C, 0, 4);
            commandEncoder.dispatch(
                { width: Math.ceil(M / 64), height: Math.ceil(N / 64), depth: 1 },
                { width: 8, height: 8, depth: 1 }
            );
            commandEncoder.endEncoding();
            commandBuffer.commit();
        }

        export function sgemmNaive(M: number, N: number, K: number, alpha: number, A: WebGPUBuffer, B: WebGPUBuffer, beta: number, C: WebGPUBuffer) {
            let MNKBuffer = webgpu.createBuffer(new Int32Array([M, N, K]));
            let abBuffer = webgpu.createBuffer(new Float32Array([alpha, beta]));

            let commandBuffer = webgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(webgpu.getPipelineStateByName('prototype.sgemm_naive'));
            commandEncoder.setBuffer(MNKBuffer, 0, 0);
            commandEncoder.setBuffer(abBuffer, 0, 1);
            commandEncoder.setBuffer(A, 0, 2);
            commandEncoder.setBuffer(B, 0, 3);
            commandEncoder.setBuffer(C, 0, 4);
            commandEncoder.dispatch(
                { width: Math.ceil(M * N / 512), height: 1, depth: 1 },
                { width: 512, height: 1, depth: 1 }
            );
            commandEncoder.endEncoding();
            commandBuffer.commit();
        }

    }
}
