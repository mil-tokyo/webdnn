if (GPGPU.isBrowserSupported) {
    GPGPU.loadKernelByFetch(`${document.currentScript.src.split('/').slice(0, -1).join('/')}/kernels/saxpy.metal`);
}

/**
 * saxpy ( y <- a*x + y )
 * @param {number} n number of elements of vector x and y
 * @param {number} a factor
 * @param {Float32Array|WebGPUBuffer} x vector x
 * @param {Float32Array|WebGPUBuffer} y vector y
 */
function saxpy(n, a, x, y) {
    let nBuffer = GPGPU.createBuffer(new Int32Array([n]));
    let aBuffer = GPGPU.createBuffer(new Float32Array([a]));
    let xBuffer = x instanceof WebGPUBuffer ? x : GPGPU.createBuffer(x);
    let yBuffer = y instanceof WebGPUBuffer ? y : GPGPU.createBuffer(y);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('saxpy'));
    commandEncoder.setBuffer(nBuffer, 0, 0);
    commandEncoder.setBuffer(aBuffer, 0, 1);
    commandEncoder.setBuffer(xBuffer, 0, 2);
    commandEncoder.setBuffer(yBuffer, 0, 3);
    commandEncoder.dispatch({
        width: 8,
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