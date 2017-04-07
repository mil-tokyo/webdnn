namespace WebDNN {
  export class WebGPUHandler {
    private context: any;
    private commandQueue: any;
    private pipelineStates: Map<string, any>;

    constructor() {
    }

    async init() {
      // asynchronous operation may be added in future
      this.context = document.createElement('canvas').getContext('webgpu');
      this.commandQueue = this.context.createCommandQueue();
      this.pipelineStates = new Map();
    }

    createBuffer(arrayBuffer: ArrayBufferView) {
      return this.context.createBuffer(arrayBuffer);
    }

    loadKernel(librarySource: string, namespace: string = '') {
      let library = this.context.createLibrary(librarySource);

      for (let name of library.functionNames) {
        let kernelFunction = library.functionWithName(name);
        let pipelineStates = this.context.createComputePipelineState(kernelFunction);

        this.pipelineStates.set(namespace + '.' + name, pipelineStates);
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
  }
}
