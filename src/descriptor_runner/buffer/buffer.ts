/**
 * @module webdnn
 */
/** Don't Remove This comment block */

/**
 * Abstract buffer interface. Read/write transactions are regarded as asynchronous operation.
 *
 * @protected
 */
export abstract class Buffer {
    /**
     * @property {number}
     */
    byteLength: number;
    backend: string;

    constructor(byteLength: number, backend: string) {
        this.byteLength = byteLength;
        this.backend = backend;
    }

    /**
     * Write contents onto specified position synchronously.
     *
     * @param {ArrayBufferView} src contents source buffer
     * @param {number} offset position where contents are written on
     */
    abstract write(src: ArrayBufferView, offset?: number): Promise<void>;

    /**
     * Read contents from specified position synchronously.
     *
     * @param {Float32ArrayConstructor | Int32ArrayConstructor} dst buffer where contents are written on
     * @param {number} offset position where contents are read from
     * @param {length} length contents length
     */
    abstract read(dst: Float32ArrayConstructor | Int32ArrayConstructor, offset?: number, length?: number): Promise<void>;

    /**
     * for a range which will be written from CPU iteratively, make view to avoid copy (if backend allows)
     * if backend does not allow such operation, return newly allocated memory and send their contents to GPU when syncWriteViews is called
     *
     * @param {number} offset position where buffer-view begin from
     * @param {number} length buffer-view length
     * @param {Int32ArrayConstructor|Float32ArrayConstructor} type data format such as Float32Array, Int32Array, and so on.
     */
    abstract getWriteView(offset?: number, length?: number, type?: Int32ArrayConstructor): Int32Array;
    abstract getWriteView(offset?: number, length?: number, type?: Float32ArrayConstructor): Float32Array;

    /**
     * for a range which will be read from CPU iteratively, make view to avoid copy (if backend allows)
     * if backend does not allow such operation, return newly allocated memory and fill their contents from GPU when syncReadViews is called
     *
     * @param {number} offset position where buffer-view begin from
     * @param {number} length buffer-view length
     * @param {Int32ArrayConstructor|Float32ArrayConstructor} type data format such as Float32Array, Int32Array, and so on.
     */
    abstract getReadView(offset?: number, length?: number, type?: Int32ArrayConstructor): Int32Array;
    abstract getReadView(offset?: number, length?: number, type?: Float32ArrayConstructor): Float32Array;

    /**
     * Sync buffered data into memory.
     *
     * @see Buffer#getWriteView
     */
    abstract syncWriteViews(): Promise<void>;

    /**
     * Sync memory data into buffer view.
     *
     * @see Buffer#getReadView
     */
    abstract syncReadViews(): Promise<void>;
}
