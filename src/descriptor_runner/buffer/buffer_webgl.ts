/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { ChannelMode } from "../graph_descriptor/graph_descriptor_webgl";
import { Buffer } from "./buffer";

/**
 * @protected
 */
const READ_TEXTURE_UNIT_INDEX_NO_BOUND = -1;

/**
 * @protected
 */
export class BufferWebGL extends Buffer {
    private gl: WebGLRenderingContext;
    readonly channelMode: ChannelMode;
    readonly elementsPerPixel: number;
    readonly array: Float32Array;
    readonly textureWidth: number;
    readonly textureHeight: number;
    private _texture: WebGLTexture | null = null;
    readonly name: string;
    private readTextureUnitIndex: number = READ_TEXTURE_UNIT_INDEX_NO_BOUND;
    private isBoundToReadFrameBuffer: boolean = false;
    private isBoundToDrawFrameBuffer: boolean = false;

    constructor(gl: WebGLRenderingContext, byteLength: number, name: string, array: Float32Array | null, channelMode: ChannelMode) {
        super(byteLength, 'webgl');
        this.gl = gl;
        this.name = name;
        this.channelMode = channelMode;
        switch (this.channelMode) {
            case 'RGBA':
                this.elementsPerPixel = 4;
                break;

            case 'R':
                this.elementsPerPixel = 1;
                break;

            default:
                throw Error('Unknown channel mode');
        }

        this.array = array || new Float32Array(this.length);

        // width is fixed as 1024, height is flexible.
        // FIXME: flexible width for efficient memory allocation
        const packedLength = Math.ceil(this.length / this.elementsPerPixel);
        this.textureWidth = packedLength <= 2048 ? packedLength : 2048;
        this.textureHeight = Math.ceil(packedLength / 2048);
    }

    get texture() {
        return this._texture;
    }

    get length(): number {
        return this.byteLength / Float32Array.BYTES_PER_ELEMENT;
    }

    /**
     * Write contents onto specified position synchronously.
     *
     * @param {ArrayBufferView} src contents source buffer
     * @param {number} offset position where contents are written on
     */
    async write(src: ArrayBufferView, offset?: number) {
        this.array.set(src as Float32Array, offset);

        await this.syncWriteViews();
    }

    /**
     * Read contents from specified position synchronously.
     *
     * @param {Float32ArrayConstructor | Int32ArrayConstructor} dst buffer where contents are written on
     * @param {number} offset position where contents are read from
     * @param {length} length contents length
     */
    async read(dst: Float32ArrayConstructor | Int32ArrayConstructor, offset: number = 0, length?: number): Promise<void> {
        if (dst !== Float32Array) throw new Error('Currently, only Float32Array is supported for parameter \'dst\'.');

        await this.syncReadViews();
        new Float32Array(this.array.buffer, offset * Float32Array.BYTES_PER_ELEMENT, length);
    }

    /**
     * for a range which will be written from CPU iteratively, make view to avoid copy (if backend allows)
     * if backend does not allow such operation, return newly allocated memory and send their contents to GPU when syncWriteViews is called
     *
     * @param {number} offset position where buffer-view begin from
     * @param {number} length buffer-view length
     * @param {Int32ArrayConstructor|Float32ArrayConstructor} type data format such as Float32Array, Int32Array, and so on.
     */
    getWriteView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
    getWriteView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
    getWriteView(offset: number, length: number, type): any {
        return new type(this.array.buffer, offset * type.BYTES_PER_ELEMENT, length);
    };

    /**
     * for a range which will be read from CPU iteratively, make view to avoid copy (if backend allows)
     * if backend does not allow such operation, return newly allocated memory and fill their contents from GPU when syncReadViews is called
     *
     * @param {number} offset position where buffer-view begin from
     * @param {number} length buffer-view length
     * @param {Int32ArrayConstructor|Float32ArrayConstructor} type data format such as Float32Array, Int32Array, and so on.
     */
    getReadView(offset: number, length: number, type: Int32ArrayConstructor): Int32Array;
    getReadView(offset: number, length: number, type: Float32ArrayConstructor): Float32Array;
    getReadView(offset: number, length: number, type): any {
        return new type(this.array.buffer, offset * type.BYTES_PER_ELEMENT, length);
    }

    /**
     * Sync buffered data into memory.
     *
     * @see Buffer#getWriteView
     */
    async syncWriteViews(): Promise<void> {
        let gl = this.gl;
        if (!this.texture) this.allocateTexture();

        let tmp = this.pack(this.array);
        if (tmp.length != this.textureWidth * this.textureHeight * 4) { //TODO
            let tmp2 = new Float32Array(this.textureWidth * this.textureHeight * 4); //TODO
            tmp2.set(tmp, 0);
            tmp = tmp2;
        }

        this.bindToReadTexture(9); //TODO: texture unit 9 is always available?
        gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, this.textureWidth, this.textureHeight, gl.RGBA, gl.FLOAT, tmp);
        this.unbindFromReadTexture();
    }

    /**
     * Sync memory data into buffer view.
     *
     * @see Buffer#getReadView
     */
    async syncReadViews(): Promise<void> {
        let gl = this.gl;
        let tmp = new Float32Array(this.textureWidth * this.textureHeight * 4); //TODO

        this.bindToDrawTexture();
        gl.readPixels(0, 0, this.textureWidth, this.textureHeight, gl.RGBA, gl.FLOAT, tmp);
        this.unbindFromDrawTexture();

        tmp = this.unpack(tmp);
        this.array.set(tmp.slice(0, this.length), 0);
    }

    async bindToReadTexture(unit: number) {
        if (this.isBoundToReadFrameBuffer)
            throw Error('This buffer is already registered as read buffer with different texture unit. ' +
                'You may forgot to unbind the binding while previous operations');

        if (this.isBoundToDrawFrameBuffer)
            throw Error('This buffer is already registered as draw buffer. ' +
                'You may forgot to unbind the binding while previous operations.');

        let gl = this.gl;
        if (!this.texture) {
            this.allocateTexture();
            await this.syncWriteViews();
        }

        gl.activeTexture(gl.TEXTURE0 + unit);
        gl.bindTexture(gl.TEXTURE_2D, this.texture);

        this.isBoundToReadFrameBuffer = true;
        this.readTextureUnitIndex = unit;
    }

    unbindFromReadTexture() {
        if (!this.isBoundToReadFrameBuffer) return;
        let gl = this.gl;

        gl.activeTexture(gl.TEXTURE0 + this.readTextureUnitIndex);
        gl.bindTexture(gl.TEXTURE_2D, null);

        this.isBoundToReadFrameBuffer = false;
        this.readTextureUnitIndex = -1;
    }

    bindToDrawTexture() {
        if (this.isBoundToReadFrameBuffer)
            throw Error('This buffer is already registered as read buffer. ' +
                'You cannot bind a texture as both read and draw texture buffer at same time.');
        if (this.isBoundToDrawFrameBuffer)
            throw Error('This buffer is already registered as draw buffer. ' +
                'You may forgot to unbind the binding while previous operations.');

        let gl = this.gl;
        if (!this.texture) this.allocateTexture();

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.texture, 0);

        this.isBoundToDrawFrameBuffer = true;
    }

    unbindFromDrawTexture() {
        if (!this.isBoundToDrawFrameBuffer) return;

        let gl = this.gl;

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, null, 0);

        this.isBoundToDrawFrameBuffer = false;
    }

    private pack(array: Float32Array) {
        switch (this.channelMode) {
            case 'RGBA':
                return new Float32Array(array);

            case 'R':
                let result = new Float32Array(array.length * 4);
                for (let i = 0; i < array.length; i++) result[i * 4] = array[i];
                return result;

            default:
                throw Error('Unknown channel mode');
        }
    }

    private unpack(array: Float32Array) {
        switch (this.channelMode) {
            case 'RGBA':
                return new Float32Array(array);

            case 'R':
                let result = new Float32Array(array.length / 4);
                for (let i = 0; i < array.length / 4; i++) result[i] = array[i * 4];
                return result;

            default:
                throw Error('Unknown channel mode');
        }
    }

    private allocateTexture() {
        if (this.texture) throw Error('Texture is already allocated.');

        this._texture = TextureManager.allocate(this.textureWidth, this.textureHeight);
    }
}

export const TextureManager = new class TextureManagerConstructor {
    private gl: WebGLRenderingContext;

    init(gl: WebGLRenderingContext) {
        this.gl = gl;
    }

    allocate(textureWidth: number, textureHeight: number): WebGLTexture {
        let gl = this.gl;
        let texture = gl.createTexture();
        if (!texture) throw Error('Texture allocation is failed.');

        gl.activeTexture(gl.TEXTURE0 + 9); // TODO: texture unit 9 is always available?
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, textureWidth, textureHeight, 0, gl.RGBA, gl.FLOAT, null);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.bindTexture(gl.TEXTURE_2D, null);

        return texture;
    }

    release(texture: WebGLTexture) {
        this.gl.deleteTexture(texture);
    }
}();
