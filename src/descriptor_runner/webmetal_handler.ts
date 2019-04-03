///<reference path="./webmetal.ts" />

/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import BufferWebMetal from "./buffer/buffer_webmetal";

/**
 * @private
 */
let instance: WebMetalHandler;

/**
 * @protected
 */
export default class WebMetalHandler {
    private context: WebMetalRenderingContext;
    private commandQueue: WebMetalCommandQueue;
    private pipelineStates: Map<string, WebMetalComputePipelineState> = new Map();
    private commandBuffer: WebMetalCommandBuffer | null;

    static getInstance() {
        if (!instance) instance = new WebMetalHandler();
        return instance;
    }

    /**
     * WebGPUHandler is singleton class and instantiate directly is forbidden (constructor is hidden).
     *
     * Since the number of GPU contexts may be limited, the handler is used as a singleton
     * and only one context is shared among multiple runners.
     */
    private constructor() {
        if (!IS_WEBMETAL_SUPPORTED) throw new Error('This browser does not support WebGPU');

        let context: WebMetalRenderingContext | null;
        try {
            context = document.createElement('canvas').getContext('webmetal');
        } catch (err) {
            throw new Error(`During initializing WebGPURenderingContext, unexpected error is occurred: ${err.message}`);
        }
        if (!context) throw new Error('WebGPURenderingContext initialization failed');

        this.context = context;
        this.commandQueue = context.createCommandQueue();

        this.loadKernel('kernel void sync(){}', 'basic');
    }

    createBuffer(arrayBuffer: ArrayBufferView): WebMetalBuffer {
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

    createCommandBuffer(): WebMetalCommandBuffer {
        return this.commandQueue.createCommandBuffer();
    }

    getPipelineStateByName(name: string): WebMetalComputePipelineState {
        let state = this.pipelineStates.get(name);
        if (!state) {
            throw TypeError(`Kernel function "${name}" is not loaded.`);
        }
        return state;
    }

    executeSinglePipelineState(name: string,
                               threadgroupsPerGrid: WebMetalSize,
                               threadsPerThreadgroup: WebMetalSize,
                               buffers: (WebMetalBuffer | BufferWebMetal)[],
                               getCompletedPromise?: boolean): Promise<void> | null {
        let commandBuffer = this.commandBuffer || (this.commandBuffer = this.createCommandBuffer());
        let commandEncoder = commandBuffer.createComputeCommandEncoder();

        commandEncoder.setComputePipelineState(this.getPipelineStateByName(name));
        for (let i = 0; i < buffers.length; i++) {
            let buffer = buffers[i];
            let wgbuf: WebMetalBuffer;
            if (buffer instanceof BufferWebMetal) {
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

        this.commandBuffer = null;

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
 * Flag whether WebMetal is supported or not
 * @protected
 */
export const IS_WEBMETAL_SUPPORTED = 'WebMetalRenderingContext' in window && 'WebMetalComputeCommandEncoder' in window;
