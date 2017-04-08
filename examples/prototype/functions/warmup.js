if (GPGPU.isBrowserSupported) {
    GPGPU.loadKernelByFetch(`${document.currentScript.src.split('/').slice(0, -1).join('/')}/kernels/warmup.metal`);
}

function warmup() {
    let dummyBuffer = GPGPU.createBuffer(new Float32Array(128 * 512));
    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('warmup'));
    commandEncoder.setBuffer(dummyBuffer, 0, 0);
    commandEncoder.dispatch({
        width: 128,
        height: 1,
        depth: 1
    }, {
        width: 512,
        height: 1,
        depth: 1
    });
    commandEncoder.endEncoding();
    commandBuffer.commit();
}