/// <reference path="./dnn_buffer_gpu.ts" />

namespace WebDNN {
  export class DNNBufferWebGPU extends DNNBufferGPU {
    private static webgpuHandler: WebGPUHandler;
    bufferView: Uint8Array;

    constructor(byteLength: number) {
      super(byteLength);
      if (byteLength == 0) {
        byteLength = 4;//0 length buffer causes error
      }
      this.backend = 'webgpu';
      this.buffer = DNNBufferWebGPU.webgpuHandler.createBuffer(new Uint8Array(byteLength));
      this.bufferView = new Uint8Array(this.buffer.contents);//can read / write GPU memory
    }

    // async: there may be platforms synchronization is needed before writing
    async write(src: ArrayBufferView, dst_offset?: number): Promise<void> {
      await DNNBufferWebGPU.webgpuHandler.sync();
      let viewSameType = new (<any>src.constructor)(this.bufferView.buffer);
      viewSameType.set(src, dst_offset);
    }

    async read<T extends ArrayBufferView>(dst: T, src_offset: number = 0, length?: number): Promise<void> {
      if (!dst) {
        throw new Error('dst cannot be null');
      }
      await DNNBufferWebGPU.webgpuHandler.sync();
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
  }
}
