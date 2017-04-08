if (GPGPU.isBrowserSupported) {
    GPGPU.loadKernelByFetch(`${document.currentScript.src.split('/').slice(0, -1).join('/')}/kernels/elementwise.metal`);
}

function inplaceRelu(n, x) {
    let nBuffer = GPGPU.createBuffer(new Int32Array([n]));
    let xBuffer = x instanceof WebGPUBuffer ? x : GPGPU.createBuffer(x);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('relu_inplace'));
    commandEncoder.setBuffer(nBuffer, 0, 0);
    commandEncoder.setBuffer(xBuffer, 0, 1);
    commandEncoder.dispatch({
        width: Math.ceil(n / 512),
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

function inplaceFixedBN(n, x) {
    let nBuffer = GPGPU.createBuffer(new Int32Array([n]));
    let xBuffer = x instanceof WebGPUBuffer ? x : GPGPU.createBuffer(x);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('bn_fixed_inplace'));
    commandEncoder.setBuffer(nBuffer, 0, 0);
    commandEncoder.setBuffer(xBuffer, 0, 1);
    commandEncoder.dispatch({
        width: Math.ceil(n / 512),
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

function inplaceReluAndFixedBN(n, x) {
    let nBuffer = GPGPU.createBuffer(new Int32Array([n]));
    let xBuffer = x instanceof WebGPUBuffer ? x : GPGPU.createBuffer(x);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('relu_and_bn_fixed_inplace'));
    commandEncoder.setBuffer(nBuffer, 0, 0);
    commandEncoder.setBuffer(xBuffer, 0, 1);
    commandEncoder.dispatch({
        width: Math.ceil(n / 512),
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