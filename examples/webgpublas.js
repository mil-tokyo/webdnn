(() => {
    class WebGPUBLAS {
        constructor(gpu) {
            this.gpgpu = gpu;
        }

        saxpy(n, a, x, y) {
            let nBuffer = this.gpgpu.createBuffer(new Int32Array([n]));
            let aBuffer = this.gpgpu.createBuffer(new Float32Array([a]));
            let xBuffer = x instanceof WebGPUBuffer ? x : this.gpgpu.createBuffer(x);
            let yBuffer = y instanceof WebGPUBuffer ? y : this.gpgpu.createBuffer(y);

            let commandBuffer = this.gpgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(this.gpgpu.getPipelineStateByName('saxpy'));
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
        sgemm(M, N, K, alpha, A, B, beta, C) {
            let MNKBuffer = this.gpgpu.createBuffer(new Int32Array([M, N, K]));
            let abBuffer = this.gpgpu.createBuffer(new Float32Array([alpha, beta]));
            let ABuffer = A instanceof WebGPUBuffer ? A : this.gpgpu.createBuffer(A);
            let BBuffer = B instanceof WebGPUBuffer ? B : this.gpgpu.createBuffer(B);
            let CBuffer = C instanceof WebGPUBuffer ? C : this.gpgpu.createBuffer(C);

            let commandBuffer = this.gpgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(this.gpgpu.getPipelineStateByName('sgemm64'));
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
        sgemmNaive(M, N, K, alpha, A, B, beta, C) {
            let MNKBuffer = this.gpgpu.createBuffer(new Int32Array([M, N, K]));
            let abBuffer = this.gpgpu.createBuffer(new Float32Array([alpha, beta]));
            let ABuffer = A instanceof WebGPUBuffer ? A : this.gpgpu.createBuffer(A);
            let BBuffer = B instanceof WebGPUBuffer ? B : this.gpgpu.createBuffer(B);
            let CBuffer = C instanceof WebGPUBuffer ? C : this.gpgpu.createBuffer(C);

            let commandBuffer = this.gpgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(this.gpgpu.getPipelineStateByName('sgemm_naive'));
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

        sync() {
            let commandBuffer = this.gpgpu.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(this.gpgpu.getPipelineStateByName('sync'));
            commandEncoder.dispatch({
                width: 1,
                height: 1,
                depth: 1
            }, {
                width: 1,
                height: 1,
                depth: 1
            });
            commandEncoder.endEncoding();
            let promise = commandBuffer.completed();
            commandBuffer.commit();

            return promise;
        }
    }

    window.initWebGPUBLAS = async function (gpu) {
        let blas = new WebGPUBLAS(gpu);

        await Promise.all([
            gpu.loadKernelByFetch('./kernels/sgemm.metal'),
            gpu.loadKernelByFetch('./kernels/saxpy.metal'),
            gpu.loadKernelByFetch('./kernels/sync.metal')
        ]);

        return blas;
    };
})();