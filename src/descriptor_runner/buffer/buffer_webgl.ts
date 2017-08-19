/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { Buffer } from "./buffer";

/**
 * @protected
 */
export class BufferWebGL extends Buffer {
    protected texture: WebGLTexture;
    protected array: Float32Array; // FIXME: support other type

    /** Once `gl.texImage2D` is called, this flag is set as `true` */
    private flagAllocatedOnGPU: boolean = false;
    private gl: WebGLRenderingContext;
    private width: number;
    private height: number;

    constructor(gl: WebGLRenderingContext, byteLength: number) {
        super(byteLength, 'webgl');
        if (byteLength % 4 !== 0) throw Error('\'byteLength\' parameter must be multiples of 4');

        this.byteLength = byteLength;
        this.array = new Float32Array(byteLength / 4);

        //FIXME
        this.width = byteLength / 4;
        this.height = 1;
    }

    get length(): number {
        return this.byteLength / 4;
    }

    /**
     * Write contents onto specified position.
     *
     * @param {ArrayBufferView} src contents source buffer
     * @param {number} offset position where contents are written on
     */
    write(src: ArrayBufferView, offset?: number): Promise<void> {
        //FIXME
        throw Error('NIY');
    }

    /**
     * Read contents from specified position.
     *
     * @param {Float32ArrayConstructor | Int32ArrayConstructor} dst buffer where contents are written on
     * @param {number} offset position where contents are read from
     * @param {length} length contents length
     */
    read(dst: Float32ArrayConstructor | Int32ArrayConstructor, offset?: number, length?: number): Promise<void> {
        //FIXME
        throw Error('NIY');
    }

    getWriteView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
    getWriteView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
    getWriteView(offset: number, length: number, type): any {
        //FIXME
        throw Error('NIY');
    };

    getReadView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
    getReadView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
    getReadView(offset: number, length: number, type): any {
        //FIXME
        throw Error('NIY');
    }

    /**
     * Sync buffered data into memory.
     *
     * @see Buffer#getWriteView
     */
    async syncWriteViews(): Promise<void> {
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.texture);

        //Pack all data into R channel
        let tmp = new Float32Array(this.length * 4);
        for (let i = 0; i < this.length; i++) tmp[i * 4] = this.array[i];

        if (this.flagAllocatedOnGPU) {
            this.gl.texSubImage2D(this.gl.TEXTURE_2D, 0, 0, 0, this.width, this.height,
                this.gl.RGBA, this.gl.FLOAT, tmp);

        } else {
            this.gl.texImage2D(this.gl.TEXTURE_2D, 0, this.gl.RGBA, this.width, this.height, 0,
                this.gl.RGBA, this.gl.FLOAT, tmp);
            this.flagAllocatedOnGPU = true;
        }
    }

    /**
     * Sync memory data into buffer view.
     *
     * @see Buffer#getReadView
     */
    async syncReadViews(): Promise<void> {
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.texture);

        let tmp = new Float32Array(this.length * 4);
        this.gl.readPixels(0, 0, this.width, this.height, this.gl.RGBA, this.gl.FLOAT, tmp);
        for (let i = 0; i < this.length; i++) this.array[i] = tmp[i * 4];
    }
}
