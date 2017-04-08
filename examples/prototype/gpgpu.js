(() => {
    const isGPGPUBrowserSupported = 'WebGPURenderingContext' in window;

    const GPGPU = new class {
        constructor() {
            if (!isGPGPUBrowserSupported) return;

            this.context = document.createElement('canvas').getContext('webgpu');
            this.commandQueue = this.context.createCommandQueue();
            this.pipelineStates = new Map();

            this.loadKernel('kernel void sync(){}');
            this.loaded = Promise.resolve();
        }

        async loadKernelByFetch(path) {
            let res = await fetch(path);
            let source = await res.text();

            let promise = this.loadKernel(source);
            this.loaded = Promise.all([promise, this.loaded]);

            return promise;
        }

        loadKernel(librarySource) {
            let library = this.context.createLibrary(librarySource);

            for (let name of library.functionNames) {
                let kernelFunction = library.functionWithName(name);
                let pipelineStates = this.context.createComputePipelineState(kernelFunction);

                this.pipelineStates.set(name, pipelineStates);
            }
        }

        createCommandBuffer() {
            return this.commandQueue.createCommandBuffer();
        }

        getPipelineStateByName(name) {
            if (!this.pipelineStates.has(name)) {
                throw TypeError(`Kernel function "${name}" is not loaded.`);
            }

            return this.pipelineStates.get(name);
        }

        createBuffer(arrayBuffer) {
            return this.context.createBuffer(arrayBuffer);
        }

        async sync() {
            let commandBuffer = this.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(this.getPipelineStateByName('sync'));
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
            let promise = commandBuffer.completed;
            commandBuffer.commit();

            return promise;
        }
    }

    Object.defineProperty(GPGPU, 'isBrowserSupported', {
        enumerable: true,
        configurable: false,
        writable: false,
        value: isGPGPUBrowserSupported
    });

    Object.defineProperty(window, 'GPGPU', {
        enumerable: true,
        configurable: false,
        writable: false,
        value: GPGPU
    });
})();