if (GPGPU.isBrowserSupported) {
    GPGPU.loadKernelByFetch(`${document.currentScript.src.split('/').slice(0, -1).join('/')}/kernels/sgemm.metal`);
}

/**
 * sgemm ( C <- alpha*A*B + beta*C )
 * @param {number} M number of rows of matrix A
 * @param {number} N number of columns of matrix B
 * @param {number} K number of rows of matrix A and columns of matrix B
 * @param {number} alpha factor alpha
 * @param {Float32Array|WebGPUBuffer} A matrix A
 * @param {Float32Array|WebGPUBuffer} B matrix B
 * @param {number} beta factor beta
 * @param {Float32Array|WebGPUBuffer} C matrix C
 */
function sgemm(M, N, K, alpha, A, B, beta, C) {
    let MNKBuffer = GPGPU.createBuffer(new Int32Array([M, N, K]));
    let abBuffer = GPGPU.createBuffer(new Float32Array([alpha, beta]));
    let ABuffer = A instanceof WebGPUBuffer ? A : GPGPU.createBuffer(A);
    let BBuffer = B instanceof WebGPUBuffer ? B : GPGPU.createBuffer(B);
    let CBuffer = C instanceof WebGPUBuffer ? C : GPGPU.createBuffer(C);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('sgemm64'));
    commandEncoder.setBuffer(MNKBuffer, 0, 0);
    commandEncoder.setBuffer(abBuffer, 0, 1);
    commandEncoder.setBuffer(ABuffer, 0, 2);
    commandEncoder.setBuffer(BBuffer, 0, 3);
    commandEncoder.setBuffer(CBuffer, 0, 4);
    commandEncoder.dispatch({
        width: Math.ceil(M / 64),
        height: Math.ceil(N / 64),
        depth: 1
    }, {
        width: 8,
        height: 8,
        depth: 1
    });
    commandEncoder.endEncoding();
    commandBuffer.commit();
}

/**
 * sgemm ( C <- alpha*A*B + beta*C )
 * @param {number} M number of rows of matrix A
 * @param {number} N number of columns of matrix B
 * @param {number} K number of rows of matrix A and columns of matrix B
 * @param {number} alpha factor alpha
 * @param {Float32Array|WebGPUBuffer} A matrix A
 * @param {Float32Array|WebGPUBuffer} B matrix B
 * @param {number} beta factor beta
 * @param {Float32Array|WebGPUBuffer} C matrix C
 */
function sgemmNaive(M, N, K, alpha, A, B, beta, C) {
    let MNKBuffer = GPGPU.createBuffer(new Int32Array([M, N, K]));
    let abBuffer = GPGPU.createBuffer(new Float32Array([alpha, beta]));
    let ABuffer = A instanceof WebGPUBuffer ? A : GPGPU.createBuffer(A);
    let BBuffer = B instanceof WebGPUBuffer ? B : GPGPU.createBuffer(B);
    let CBuffer = C instanceof WebGPUBuffer ? C : GPGPU.createBuffer(C);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('sgemm_naive'));
    commandEncoder.setBuffer(MNKBuffer, 0, 0);
    commandEncoder.setBuffer(abBuffer, 0, 1);
    commandEncoder.setBuffer(ABuffer, 0, 2);
    commandEncoder.setBuffer(BBuffer, 0, 3);
    commandEncoder.setBuffer(CBuffer, 0, 4);
    commandEncoder.dispatch({
        width: Math.ceil(M * N / 512),
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