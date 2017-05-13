declare interface WebGPURenderingContext {
    createCommandQueue(): WebGPUCommandQueue;
    createBuffer(data: ArrayBufferView): WebGPUBuffer;
    createLibrary(sourceCode: string): WebGPULibrary;
    createComputePipelineState(function_: WebGPUFunction): WebGPUComputePipelineState;
}

declare interface WebGPUFunction {
}

declare interface WebGPULibrary {
    functionNames: string[];
    functionWithName(name: string): WebGPUFunction;
}

declare interface WebGPUBuffer {
    contents: any;
}

declare interface WebGPUSize {
    width: number;
    height: number;
    depth: number;
}

declare interface WebGPUCommandQueue {
    createCommandBuffer(): WebGPUCommandBuffer;
}

declare interface WebGPUCommandBuffer {
    createComputeCommandEncoder(): WebGPUComputeCommandEncoder;
    commit(): void;
    completed: Promise<void>;
}

declare interface WebGPUCommandEncoder {
    endEncoding(): void;
}

declare interface WebGPUComputeCommandEncoder extends WebGPUCommandEncoder {
    setComputePipelineState(state: WebGPUComputePipelineState): void;
    setBuffer(buffer: WebGPUBuffer, offset: number, index: number): void;
    dispatch(threadgroupsPerGrid: WebGPUSize, threadsPerThreadgroup: WebGPUSize): void;
}

declare interface WebGPUComputePipelineState {
}
