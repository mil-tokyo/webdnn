interface WebGPURenderingContext {
    createCommandQueue(): WebGPUCommandQueue;

    createBuffer(data: ArrayBufferView): WebGPUBuffer;

    createLibrary(sourceCode: string): WebGPULibrary;

    createComputePipelineState(function_: WebGPUFunction): WebGPUComputePipelineState;
}

interface WebGPUFunction {
}

interface WebGPULibrary {
    functionNames: string[];

    functionWithName(name: string): WebGPUFunction;
}

interface WebGPUBuffer {
    contents: any;
}

interface WebGPUSize {
    width: number;
    height: number;
    depth: number;
}

interface WebGPUCommandQueue {
    createCommandBuffer(): WebGPUCommandBuffer;
}

interface WebGPUCommandBuffer {
    createComputeCommandEncoder(): WebGPUComputeCommandEncoder;

    commit(): void;

    completed: Promise<void>;
}

interface WebGPUCommandEncoder {
    endEncoding(): void;
}

interface WebGPUComputeCommandEncoder extends WebGPUCommandEncoder {
    setComputePipelineState(state: WebGPUComputePipelineState): void;

    setBuffer(buffer: WebGPUBuffer, offset: number, index: number): void;

    dispatch(threadgroupsPerGrid: WebGPUSize, threadsPerThreadgroup: WebGPUSize): void;
}

interface WebGPUComputePipelineState {
}

interface HTMLCanvasElement {
    getContext(contextId: "webgpu"): WebGPURenderingContext | null;
}
