interface WebMetalRenderingContext {
    createCommandQueue(): WebMetalCommandQueue;

    createBuffer(data: ArrayBufferView): WebMetalBuffer;

    createLibrary(sourceCode: string): WebMetalLibrary;

    createComputePipelineState(function_: WebMetalFunction): WebMetalComputePipelineState;
}

interface WebMetalFunction {
}

interface WebMetalLibrary {
    functionNames: string[];

    functionWithName(name: string): WebMetalFunction;
}

interface WebMetalBuffer {
    contents: any;
}

interface WebMetalSize {
    width: number;
    height: number;
    depth: number;
}

interface WebMetalCommandQueue {
    createCommandBuffer(): WebMetalCommandBuffer;
}

interface WebMetalCommandBuffer {
    createComputeCommandEncoder(): WebMetalComputeCommandEncoder;

    commit(): void;

    completed: Promise<void>;
}

interface WebMetalCommandEncoder {
    endEncoding(): void;
}

interface WebMetalComputeCommandEncoder extends WebMetalCommandEncoder {
    setComputePipelineState(state: WebMetalComputePipelineState): void;

    setBuffer(buffer: WebMetalBuffer, offset: number, index: number): void;

    dispatch(threadgroupsPerGrid: WebMetalSize, threadsPerThreadgroup: WebMetalSize): void;
}

interface WebMetalComputePipelineState {
}

interface HTMLCanvasElement {
    getContext(contextId: "webmetal"): WebMetalRenderingContext | null;
}
