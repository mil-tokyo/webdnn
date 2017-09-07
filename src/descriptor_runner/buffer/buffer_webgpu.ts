/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import WebGPUHandler from "../webgpu_handler";
import { Buffer } from "./buffer";

/**
 * @protected
 */
export default class BufferWebGPU extends Buffer {
    private static handler: WebGPUHandler;
    buffer: WebGPUBuffer;
    bufferView: Uint8Array;

    constructor(byteLength: number) {
        super(byteLength, 'webgpu');
        if (byteLength == 0) {
            byteLength = 4;//0 length buffer causes error
        }
        this.buffer = BufferWebGPU.handler.createBuffer(new Uint8Array(byteLength));
        this.bufferView = new Uint8Array(this.buffer.contents);
    }

    // async: there may be platforms synchronization is needed before writing
    async write(src: ArrayBufferView, dst_offset?: number): Promise<void> {
        await BufferWebGPU.handler.sync();
        let viewSameType = new (<any>src.constructor)(this.bufferView.buffer);
        viewSameType.set(src, dst_offset);
    }

    async read(dst: any, src_offset: number = 0, length?: number): Promise<void> {
        if (!dst) throw new Error('dst cannot be null');

        await BufferWebGPU.handler.sync();
        if (this.byteLength === 0) return;

        let dstConstructor = dst.constructor;
        let viewSameType = new dstConstructor(this.bufferView.buffer, this.bufferView.byteOffset + src_offset * dstConstructor.BYTES_PER_ELEMENT, length);

        dst.set(viewSameType);
        return;
    }

    static init(webgpuHandler: WebGPUHandler) {
        this.handler = webgpuHandler;
    }

    getWriteView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
    getWriteView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
    getWriteView(offset: number, length: number, type): any {
        return new type(this.bufferView.buffer, this.bufferView.byteOffset + offset * type.BYTES_PER_ELEMENT, length);
    }

    getReadView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
    getReadView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
    getReadView(offset: number, length: number, type): any {
        return new type(this.bufferView.buffer, this.bufferView.byteOffset + offset * type.BYTES_PER_ELEMENT, length);
    }

    async syncWriteViews(): Promise<void> {
        // no sync needed
    }

    async syncReadViews(): Promise<void> {
        // if the user awaits promise from final kernel execution, this function call is not needed.
        await BufferWebGPU.handler.sync();
    }
}
