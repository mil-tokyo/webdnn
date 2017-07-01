/// <reference path="./buffer/buffer_webgpu.ts" />

namespace WebDNN {
    export class WebGPUHandler {
        static isBrowserSupported: boolean;
        private context: WebGPURenderingContext;
        private commandQueue: WebGPUCommandQueue;
        private pipelineStates: Map<string, WebGPUComputePipelineState>;

        async init() {
            if (!WebGPUHandler.isBrowserSupported) throw new Error('This browser does not support WebGPU');

            let context = document.createElement('canvas').getContext('webgpu');
            if (!context) throw new Error('WebGPURenderingContext initialization failed');

            this.context = context;

            this.commandQueue = context.createCommandQueue();
            this.pipelineStates = new Map();
        }

        createBuffer(arrayBuffer: ArrayBufferView): WebGPUBuffer {
            return this.context.createBuffer(arrayBuffer);
        }

        loadKernel(librarySource: string, namespace: string = ''): void {
            let library = this.context.createLibrary(librarySource);

            for (let name of library.functionNames) {
                let kernelFunction = library.functionWithName(name);
                let pipelineStates = this.context.createComputePipelineState(kernelFunction);

                this.pipelineStates.set(namespace + '.' + name, pipelineStates);
            }
        }

        createCommandBuffer(): WebGPUCommandBuffer {
            return this.commandQueue.createCommandBuffer();
        }

        getPipelineStateByName(name: string): WebGPUComputePipelineState {
            let state = this.pipelineStates.get(name);
            if (!state) {
                throw TypeError(`Kernel function "${name}" is not loaded.`);
            }
            return state;
        }

        executeSinglePipelineState(name: string,
                                   threadgroupsPerGrid: WebGPUSize,
                                   threadsPerThreadgroup: WebGPUSize,
                                   buffers: (WebGPUBuffer | BufferWebGPU)[],
                                   getCompletedPromise?: boolean): Promise<void> | null {
            let commandBuffer = this.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(this.getPipelineStateByName(name));
            for (let i = 0; i < buffers.length; i++) {
                let buffer = buffers[i];
                let wgbuf: WebGPUBuffer;
                if (buffer instanceof BufferWebGPU) {
                    wgbuf = buffer.buffer;
                } else {
                    // cannot perform (buffer instanceof WebGPUBuffer) currently
                    wgbuf = buffer;
                }

                commandEncoder.setBuffer(wgbuf, 0, i);
            }
            commandEncoder.dispatch(threadgroupsPerGrid, threadsPerThreadgroup);
            commandEncoder.endEncoding();
            let promise: Promise<void> | null = null;
            if (getCompletedPromise) {
                promise = commandBuffer.completed;
            }
            commandBuffer.commit();
            return promise;
        }

        async sync(): Promise<void> {
            let commandBuffer = this.createCommandBuffer();
            let commandEncoder = commandBuffer.createComputeCommandEncoder();

            commandEncoder.setComputePipelineState(this.getPipelineStateByName('basic.sync'));
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

    WebGPUHandler.isBrowserSupported = 'WebGPURenderingContext' in window && 'WebGPUComputeCommandEncoder' in window;
}

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

declare interface HTMLCanvasElement {
    getContext(contextId: "webgpu"): WebGPURenderingContext | null;
}
