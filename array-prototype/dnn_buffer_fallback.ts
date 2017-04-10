/// <reference path="./dnn_buffer_gpu.ts" />

namespace WebDNN {
  export class DNNBufferFallback extends DNNBufferGPU {
    private static webgpuHandler: WebGPUHandler;
    bufferView: Uint8Array;

    constructor(byteLength: number) {
      super(byteLength);
      this.backend = 'fallback';
      this.bufferView = new Uint8Array(byteLength);//can read / write GPU memory
      this.buffer = this.bufferView.buffer;
    }

    // async: there may be platforms synchronization is needed before writing
    async write(src: ArrayBufferView, dst_offset?: number): Promise<void> {
      let viewSameType = new (<any>src.constructor)(this.bufferView.buffer);
      viewSameType.set(src, dst_offset);
    }

    async read<T extends ArrayBufferView>(dst: T, src_offset: number = 0, length?: number): Promise<void> {
      if (!dst) {
        throw new Error('dst cannot be null');
      }

      let dst_constructor = <any>dst.constructor;//e.g. Float32Array
      let viewSameType = new dst_constructor(this.bufferView.buffer, this.bufferView.byteOffset + src_offset * dst_constructor.BYTES_PER_ELEMENT, length);

      if (length === undefined) {
        length = viewSameType.length - src_offset;
      }
      (<any>dst).set(viewSameType);
      return;
    }

  }
}
