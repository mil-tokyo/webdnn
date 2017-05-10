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

        // for a range which will be written from CPU iteratively, make view to avoid copy (if backend allows)
        // if backend does not allow such operation, return newly allocated memory and send their contents to GPU when syncWriteViews is called
        getWriteView(offset: number, length: number, number_type: any): ArrayBufferView {
            throw new Error();
        }

        // for a range which will be read from CPU iteratively, make view to avoid copy (if backend allows)
        // if backend does not allow such operation, return newly allocated memory and fill their contents from GPU when syncReadViews is called
        getReadView(offset: number, length: number, number_type: any): ArrayBufferView {
            throw new Error();
        }

        async syncWriteViews(): Promise<void> {
            // no sync needed
            throw new Error();
        }

        async syncReadViews(): Promise<void> {
            // no sync needed
            throw new Error();
        }
    }
}
