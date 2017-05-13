/// <reference path="./buffer.ts" />

namespace WebDNN {
    export class BufferWebGPU extends Buffer {
        private static webgpuHandler: WebGPUHandler;
        buffer: WebGPUBuffer;
        bufferView: Uint8Array;

        constructor(byteLength: number) {
            super(byteLength, 'webgpu');
            if (byteLength == 0) {
                byteLength = 4;//0 length buffer causes error
            }
            this.buffer = BufferWebGPU.webgpuHandler.createBuffer(new Uint8Array(byteLength));
            this.bufferView = new Uint8Array(this.buffer.contents);
        }

        // async: there may be platforms synchronization is needed before writing
        async write(src: ArrayBufferView, dst_offset?: number): Promise<void> {
            await BufferWebGPU.webgpuHandler.sync();
            let viewSameType = new (<any>src.constructor)(this.bufferView.buffer);
            viewSameType.set(src, dst_offset);
        }

        async read<T extends ArrayBufferView>(dst: T, src_offset: number = 0, length?: number): Promise<void> {
            if (!dst) {
                throw new Error('dst cannot be null');
            }
            await BufferWebGPU.webgpuHandler.sync();
            if (this.byteLength === 0) {
                // nothing to read
                return;
            }

            let dst_constructor = <any>dst.constructor;//e.g. Float32Array
            let viewSameType = new dst_constructor(this.bufferView.buffer, this.bufferView.byteOffset + src_offset * dst_constructor.BYTES_PER_ELEMENT, length);

            if (length === undefined) {
                length = viewSameType.length - src_offset;
            }
            (<any>dst).set(viewSameType);
            return;
        }

        static init(webgpuHandler: WebGPUHandler) {
            this.webgpuHandler = webgpuHandler;
        }

        getWriteView(offset: number, length: number, number_type: any): ArrayBufferView {
            let viewSameType = new number_type(this.bufferView.buffer, this.bufferView.byteOffset + offset * number_type.BYTES_PER_ELEMENT, length);
            return viewSameType;
        }

        getReadView(offset: number, length: number, number_type: any): ArrayBufferView {
            let viewSameType = new number_type(this.bufferView.buffer, this.bufferView.byteOffset + offset * number_type.BYTES_PER_ELEMENT, length);
            return viewSameType;
        }

        async syncWriteViews(): Promise<void> {
            // no sync needed
        }

        async syncReadViews(): Promise<void> {
            // if the user awaits promise from final kernel execution, this function call is not needed.
            await BufferWebGPU.webgpuHandler.sync();
        }
    }
}
