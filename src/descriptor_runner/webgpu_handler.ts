/// <reference path="./webgpu.d.ts" />
/// <reference path="./buffer/buffer_webgpu.ts" />

namespace WebDNN {
    export class WebGPUHandler {
        static isBrowserSupported: boolean;
        private context: WebGPURenderingContext;
        private commandQueue: WebGPUCommandQueue;
        private pipelineStates: Map<string, WebGPUComputePipelineState>;

        async init() {
            // asynchronous operation may be added in future
            if (!WebGPUHandler.isBrowserSupported) {
                throw new Error('This browser does not support WebGPU');
            }
            this.context = <WebGPURenderingContext>(<any>document.createElement('canvas').getContext('webgpu'));//force cast
            this.commandQueue = this.context.createCommandQueue();
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
