class GPGPU {
    constructor() {
        if (!GPGPU.isBrowserSupported) {
            throw TypeError('WebGPURenderingContext isn\'t supported in this browser.');
        }

        this.context = document.createElement('canvas').getContext('webgpu');
        this.commandQueue = this.context.createCommandQueue();
        this.pipelineStates = new Map();
    }

    async loadKernelByFetch(path) {
        let res = await fetch(path);
        let source = await res.text();

        return this.loadKernel(source);
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
}

GPGPU.isBrowserSupported = 'WebGPURenderingContext' in window;