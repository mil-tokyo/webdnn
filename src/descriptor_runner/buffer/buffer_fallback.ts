/// <reference path="../webgpu_handler.ts" />
/// <reference path="./buffer.ts" />

namespace WebDNN {
    export class BufferFallback extends Buffer {
        bufferView: Uint8Array;
        buffer: ArrayBuffer;

        constructor(byteLength: number) {
            super(byteLength, 'fallback');
            this.bufferView = new Uint8Array(byteLength);
            this.buffer = this.bufferView.buffer;
        }

        // async: there may be platforms synchronization is needed before writing
        write(src: ArrayBufferView, dst_offset?: number) {
            let viewSameType = new (<any>src.constructor)(this.bufferView.buffer);
            return Promise.resolve(viewSameType.set(src, dst_offset));
        }

        read<T extends ArrayBufferView>(dst: T, src_offset: number = 0, length?: number) {
            if (!dst) {
                throw new Error('dst cannot be null');
            }

            let dst_constructor = <any>dst.constructor;//e.g. Float32Array
            let viewSameType = new dst_constructor(this.bufferView.buffer, this.bufferView.byteOffset + src_offset * dst_constructor.BYTES_PER_ELEMENT, length);

            if (length === undefined) {
                length = viewSameType.length - src_offset;
            }
            (<any>dst).set(viewSameType);

            return Promise.resolve();
        }

        getWriteView(offset: number, length: number, number_type: any): ArrayBufferView {
            let viewSameType = new number_type(this.bufferView.buffer, this.bufferView.byteOffset + offset * number_type.BYTES_PER_ELEMENT, length);
            return viewSameType;
        }

        getReadView(offset: number, length: number, number_type: any): ArrayBufferView {
            let viewSameType = new number_type(this.bufferView.buffer, this.bufferView.byteOffset + offset * number_type.BYTES_PER_ELEMENT, length);
            return viewSameType;
        }

        syncWriteViews() {
            // no sync needed
            return Promise.resolve();
        }

        syncReadViews() {
            // no sync needed
            return Promise.resolve();
        }
    }
}
