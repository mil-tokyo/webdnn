if (GPGPU.isBrowserSupported) {
    GPGPU.loadKernelByFetch(`${document.currentScript.src.split('/').slice(0, -1).join('/')}/kernels/convolution2d.metal`);
}

class Convolution2dDescriptor {
    constructor(data) {
        this.kw = ('kernel' in data) ? ((data.kernel instanceof Array) ? data.kernel[0] : data.kernel) : 3;
        this.kh = ('kernel' in data) ? ((data.kernel instanceof Array) ? data.kernel[1] : data.kernel) : 3;
        this.sw = ('stride' in data) ? ((data.stride instanceof Array) ? data.stride[0] : data.stride) : 1;
        this.sh = ('stride' in data) ? ((data.stride instanceof Array) ? data.stride[1] : data.stride) : 1;
        this.pw = ('padding' in data) ? ((data.padding instanceof Array) ? data.padding[0] : data.padding) : 1;
        this.ph = ('padding' in data) ? ((data.padding instanceof Array) ? data.padding[1] : data.padding) : 1;
        this.batchsize = data.batchsize;
        this.w1 = (data.size instanceof Array) ? data.size[0] : data.size;
        this.h1 = (data.size instanceof Array) ? data.size[1] : data.size;
        this.c1 = (data.channels instanceof Array) ? data.channels[0] : data.channels;
        this.c2 = (data.channels instanceof Array) ? data.channels[1] : data.channels;

        this.w2 = (this.w1 + 2 * this.pw - this.kw) / this.sw + 1;
        this.h2 = (this.h1 + 2 * this.ph - this.kh) / this.sh + 1;

        this.buffer = GPGPU.createBuffer(new Int32Array([
            this.kw, this.kh, this.sw, this.sh, this.pw, this.ph,
            this.batchsize, this.w1, this.h1, this.c1, this.c2
        ]));
    }
}

/**
 * @param {Convolution2dDescriptor} desc convolution2d descriptor
 * @param {Float32Array|WebGPUBuffer} X input buffer
 * @param {Float32Array|WebGPUBuffer} W filter buffer
 * @param {Float32Array|WebGPUBuffer} Y output buffer
 */
function convolution2dNaive(desc, X, W, Y) {
    let XBuffer = X instanceof WebGPUBuffer ? X : GPGPU.createBuffer(X);
    let WBuffer = W instanceof WebGPUBuffer ? W : GPGPU.createBuffer(W);
    let YBuffer = Y instanceof WebGPUBuffer ? Y : GPGPU.createBuffer(Y);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('convolution2d_naive'));
    commandEncoder.setBuffer(desc.buffer, 0, 0);
    commandEncoder.setBuffer(XBuffer, 0, 1);
    commandEncoder.setBuffer(WBuffer, 0, 2);
    commandEncoder.setBuffer(YBuffer, 0, 3);
    commandEncoder.dispatch({
        width: Math.ceil(desc.batchsize * desc.c2 * desc.h2 * desc.w2 / 512),
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

/**
 * @param {Convolution2dDescriptor} desc convolution2d descriptor
 * @param {Float32Array|WebGPUBuffer} X input buffer
 * @param {Float32Array|WebGPUBuffer} W filter buffer
 * @param {Float32Array|WebGPUBuffer} Y output buffer
 */
function convolution2dNaiveAndRelu(desc, X, W, Y) {
    let XBuffer = X instanceof WebGPUBuffer ? X : GPGPU.createBuffer(X);
    let WBuffer = W instanceof WebGPUBuffer ? W : GPGPU.createBuffer(W);
    let YBuffer = Y instanceof WebGPUBuffer ? Y : GPGPU.createBuffer(Y);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('convolution2d_naive_and_relu'));
    commandEncoder.setBuffer(desc.buffer, 0, 0);
    commandEncoder.setBuffer(XBuffer, 0, 1);
    commandEncoder.setBuffer(WBuffer, 0, 2);
    commandEncoder.setBuffer(YBuffer, 0, 3);
    commandEncoder.dispatch({
        width: Math.ceil(desc.batchsize * desc.c2 * desc.h2 * desc.w2 / 512),
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

/**
 * @param {Convolution2dDescriptor} desc convolution2d descriptor
 * @param {Float32Array|WebGPUBuffer} X input buffer
 * @param {Float32Array|WebGPUBuffer} W filter buffer
 * @param {Float32Array|WebGPUBuffer} Y output buffer
 */
function im2col(descBuffer, im, col) {
    let imBuffer = im instanceof WebGPUBuffer ? im : GPGPU.createBuffer(im);
    let colBuffer = col instanceof WebGPUBuffer ? col : GPGPU.createBuffer(col);

    let commandBuffer = GPGPU.createCommandBuffer();
    let commandEncoder = commandBuffer.createComputeCommandEncoder();

    commandEncoder.setComputePipelineState(GPGPU.getPipelineStateByName('im2col'));
    commandEncoder.setBuffer(desc.buffer, 0, 0);
    commandEncoder.setBuffer(imBuffer, 0, 1);
    commandEncoder.setBuffer(colBuffer, 0, 2);
    commandEncoder.dispatch({
        width: Math.ceil(desc.batchSize * desc.h2 * desc.w2 * desc.c1 * desc.kh * desc.kw / 512),
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