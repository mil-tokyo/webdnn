namespace WebDNN {
  export class DNNBufferGPU {
    backend: string;
    buffer: any;

    constructor(public byteLength: number) {
    }

    // async: there may be platforms synchronization is needed before writing
    async write(src: ArrayBufferView, dst_offset?: number): Promise<void> {
      throw new Error();
    }

    async read(dst: ArrayBufferView, src_offset?: number, length?: number): Promise<void> {
      throw new Error();
    }
  }
}
