///<reference path="./webgpu.d.ts" />

/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import BufferWebGPU from "./buffer/buffer_webgpu";

/**
 * @protected
 */
export default class WebGPUHandler {
    private context: WebGPURenderingContext;
    private commandQueue: WebGPUCommandQueue;
    private pipelineStates: Map<string, WebGPUComputePipelineState> = new Map();

    constructor() {
        if (!IS_WEBGPU_SUPPORTED) throw new Error('This browser does not support WebGPU');

        let context: WebGPURenderingContext | null;
        try {
            context = document.createElement('canvas').getContext('webgpu');
        } catch (err) {
            throw new Error(`During initializing WebGPURenderingContext, unexpected error is occurred: ${err.message}`);
        }
        if (!context) throw new Error('WebGPURenderingContext initialization failed');

        this.context = context;
        this.commandQueue = context.createCommandQueue();
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

/**
 * Flag whether WebGPU is supported or not
 * @protected
 */
export const IS_WEBGPU_SUPPORTED = 'WebGPURenderingContext' in window && 'WebGPUComputeCommandEncoder' in window;
