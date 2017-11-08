/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { ChannelMode } from "../graph_descriptor/graph_descriptor_webgl";
import WebGLHandler, { isWebGL2 } from "../webgl_handler";
import { Buffer } from "./buffer";

/**
 * @protected
 */
export default class BufferWebGL extends Buffer {
    private handler: WebGLHandler;
    readonly channelMode: ChannelMode;
    readonly elementsPerPixel: number; // ex) (ChannelMode.R)=1, (ChannelMode.RGBA)=4
    readonly pixelStride: number; // ex) (R32F & ChannelMode.R)=1, (RGBA32F & ChannelMode.R)=4, (RGBA32F & ChannelMode.RGBA)=1,
    readonly array: Float32Array;
    readonly textureWidth: number;
    readonly textureHeight: number;
    readonly textureFormat: number;
    readonly textureInternalFormat: number;
    private _texture: WebGLTexture | null = null;
    readonly name: string;
    private readTextureUnitIndices: number[] = [];
    private isBoundToDrawFrameBuffer: boolean = false;

    constructor(byteLength: number, textureWidth: number, textureHeight: number,
                name: string, array: Float32Array | null, channelMode: ChannelMode) {
        super(byteLength, 'webgl');
        this.handler = WebGLHandler.getInstance();
        this.name = name;
        this.channelMode = channelMode;
        switch (channelMode) {
            case 'RGBA':
                this.elementsPerPixel = 4;
                break;

            case 'R':
                this.elementsPerPixel = 1;
                break;

            default:
                throw Error('Unknown channel mode');
        }

        if (isWebGL2(this.handler.gl)) {
            switch (channelMode) {
                case 'RGBA':
                    this.textureFormat = this.handler.gl.RGBA;
                    this.textureInternalFormat = this.handler.gl.RGBA32F;
                    this.pixelStride = 4;
                    break;

                case 'R':
                    this.textureFormat = this.handler.gl.RED;
                    this.textureInternalFormat = this.handler.gl.R32F;
                    this.pixelStride = 1;
                    break;

                default:
                    throw Error('Unknown channel mode');
            }
        } else {
            // In WebGL1, always RGBA channel mode is specified. If R channel mode is specified in graph descriptor,
            // other 3 channels are not used.
            this.textureFormat = this.handler.gl.RGBA;
            this.textureInternalFormat = this.handler.gl.RGBA;
            this.pixelStride = 4;
        }

        if (this.pixelStride < this.elementsPerPixel)
            throw Error('elementsPerPixel must be smaller than pixelStride');

        this.array = array || new Float32Array(this.length);

        this.textureWidth = textureWidth;
        this.textureHeight = textureHeight;
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
        let gl = this.handler.gl;
        if (!this.texture) this.allocateTexture();

        let tmp = this.pack(this.array);
        if (tmp.length != this.textureWidth * this.textureHeight * this.pixelStride) {
            let tmp2 = new Float32Array(this.textureWidth * this.textureHeight * this.elementsPerPixel);
            tmp2.set(tmp, 0);
            tmp = tmp2;
        }

        await this.bindToReadTexture(9); //TODO: texture unit 9 is always available?
        gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, this.textureWidth, this.textureHeight, this.textureFormat, gl.FLOAT, tmp);
        this.unbindFromReadTexture();
    }

    /**
     * Sync memory data into buffer view.
     *
     * @see Buffer#getReadView
     */
    async syncReadViews(): Promise<void> {
        let gl = this.handler.gl;

        // FIXME(Kiikurage): more readable code
        const ELEMENT_PER_PIXEL = 4;
        const FORMAT = gl.RGBA;

        let tmp = new Float32Array(this.textureWidth * this.textureHeight * ELEMENT_PER_PIXEL);

        this.bindToDrawTexture();
        gl.readPixels(0, 0, this.textureWidth, this.textureHeight, FORMAT, gl.FLOAT, tmp);
        this.unbindFromDrawTexture();

        tmp = this.unpack(tmp);
        this.array.set(tmp.slice(0, this.length), 0);
    }

    async bindToReadTexture(unit: number) {
        if (this.isBoundToDrawFrameBuffer)
            throw Error('This buffer is already registered as draw buffer. ' +
                'You may forgot to unbind the binding while previous operations.');

        let gl = this.handler.gl;
        if (!this.texture) {
            this.allocateTexture();
            await this.syncWriteViews();
        }

        gl.activeTexture(gl.TEXTURE0 + unit);
        gl.bindTexture(gl.TEXTURE_2D, this.texture);

        this.readTextureUnitIndices.push(unit);
    }

    unbindFromReadTexture() {
        let gl = this.handler.gl;

        for (let unit of this.readTextureUnitIndices) {
            gl.activeTexture(gl.TEXTURE0 + unit);
            gl.bindTexture(gl.TEXTURE_2D, null);
        }

        this.readTextureUnitIndices = [];
    }

    bindToDrawTexture() {
        if (this.readTextureUnitIndices.length > 0)
            throw Error('This buffer is already registered as read buffer. ' +
                'You cannot bind a texture as both read and draw texture buffer at same time.');
        if (this.isBoundToDrawFrameBuffer)
            throw Error('This buffer is already registered as draw buffer. ' +
                'You may forgot to unbind the binding while previous operations.');

        let gl = this.handler.gl;
        if (!this.texture) this.allocateTexture();

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.texture, 0);

        this.isBoundToDrawFrameBuffer = true;
    }

    unbindFromDrawTexture() {
        if (!this.isBoundToDrawFrameBuffer) return;

        let gl = this.handler.gl;

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, null, 0);

        this.isBoundToDrawFrameBuffer = false;
    }

    private pack(array: Float32Array) {
        let elementStride = this.pixelStride / this.elementsPerPixel;

        if (elementStride === 1) {
            return new Float32Array(array);

        } else {
            let result = new Float32Array(array.length * elementStride);
            for (let i = 0; i < array.length; i++) result[i * elementStride] = array[i];
            return result;
        }
    }

    private unpack(array: Float32Array) {
        // FIXME(Kiikurage): more readable code
        const PIXEL_STRIDE = 4;

        let elementStride = PIXEL_STRIDE / this.elementsPerPixel;
        if (elementStride === 1) {
            return new Float32Array(array);

        } else {
            let result = new Float32Array(array.length / elementStride);
            for (let i = 0; i < array.length / elementStride; i++) result[i] = array[i * elementStride];
            return result;
        }
    }

    private allocateTexture() {
        if (this.texture) throw Error('Texture is already allocated.');

        this._texture = this.handler.createTexture(
            this.textureWidth,
            this.textureHeight,
            this.textureInternalFormat,
            this.textureFormat
        );
    }
}
