namespace WebDNN {
    /**
     * Abstract buffer interface. Read/write transactions are regarded as asynchronous operation.
     */
    export abstract class Buffer {
        byteLength: number;
        backed: string;

        constructor(byteLength: number, backed: string) {
            this.byteLength = byteLength;
            this.backed = backed;
        }

        /**
         * Write contents into specified position.
         * @param src contents souce buffer.
         * @param dst_offset position where contents are written on
         */
        abstract write(src: ArrayBufferView, dst_offset?: number): Promise<void>;

        /**
         * Read contents from specified position.
         * @param dst buffer where contents are written on
         * @param src_offset position where contents are read from
         * @param length contents length
         */
        abstract read(dst: ArrayBufferView, src_offset?: number, length?: number): Promise<void>;

        /**
         * for a range which will be written from CPU iteratively, make view to avoid copy (if backend allows)
         * if backend does not allow such operation, return newly allocated memory and send their contents to GPU when syncWriteViews is called
         * @param offset position where buffer-view begin from
         * @param length buffer-view length
         * @param number_type data format such as Float32, UInt8, and so on.
         */
        abstract getWriteView(offset: number, length: number, number_type: any): ArrayBufferView;

        /**
         * for a range which will be read from CPU iteratively, make view to avoid copy (if backend allows)
         * if backend does not allow such operation, return newly allocated memory and fill their contents from GPU when syncReadViews is called
         * @param offset position where buffer-view begin from
         * @param length buffer-view length
         * @param number_type data format such as Float32, UInt8, and so on.
         */
        abstract getReadView(offset: number, length: number, number_type: any): ArrayBufferView;

        /**
         * Sync buffered data into memory.
         */
        abstract syncWriteViews(): Promise<void>;

        /**
         * Sync memory data into buffer view.
         */
        abstract syncReadViews(): Promise<void>;
    }
}
