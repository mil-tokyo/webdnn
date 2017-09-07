/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { isDebugMode } from "./webdnn";

export declare interface WebGLVertexArray {
}

/**
 * @protected
 */
export default class WebGLHandler {
    readonly gl: WebGLRenderingContext;
    readonly vao: any | null;
    readonly isWebGL2: boolean;

    constructor() {
        let {gl, vao, isWebGL2} = checkNull(WebGLHandler.initializeContext());
        this.gl = gl;
        this.vao = vao;
        this.isWebGL2 = isWebGL2;
    }

    createTexture(textureWidth: number, textureHeight: number) {
        let gl = this.gl;

        let texture = checkNull(gl.createTexture());
        let internalFormat = this.isWebGL2 ? (gl as any).R32F : gl.RGBA;
        let format = this.isWebGL2 ? (gl as any).RED : gl.RGBA;
        let type = gl.FLOAT;

        gl.activeTexture(gl.TEXTURE0 + 9); // TODO: texture unit 9 is always available?
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, textureWidth, textureHeight, 0, format, type, null);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.bindTexture(gl.TEXTURE_2D, null);

        return texture;
    }

    createVertexShader(source: string) {
        return this.createShader(this.gl.VERTEX_SHADER, source);
    }

    createFragmentShader(source: string) {
        return this.createShader(this.gl.FRAGMENT_SHADER, source);
    }

    createShader(type: number, source: string) {
        let shader = checkNull(this.gl.createShader(type));

        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);
        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            console.error(this.gl.getShaderInfoLog(shader));
            throw Error("Shader Compile failed: " + this.gl.getShaderInfoLog(shader));
        }

        return shader;
    }

    createProgram(vertexShader: WebGLShader, fragmentShader: WebGLShader) {
        let program = checkNull(this.gl.createProgram());

        this.gl.attachShader(program, fragmentShader);
        this.gl.attachShader(program, vertexShader);
        this.gl.linkProgram(program);
        if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
            console.error(this.gl.getProgramInfoLog(program));
            throw Error('ShaderProgram Initialization failed.');
        }

        return program;
    }

    createArrayBuffer(vertexArray: number | Float32Array) {
        let buffer = checkNull(this.gl.createBuffer());
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, buffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, vertexArray, this.gl.STATIC_DRAW);

        return buffer
    }

    createVertexArray(): WebGLVertexArray {
        if (this.isWebGL2) {
            return checkNull((this.gl as any).createVertexArray() as WebGLVertexArray | null);
        } else {
            return checkNull(this.vao.createVertexArrayOES() as WebGLVertexArray | null);
        }
    }

    createFrameBuffer(): WebGLFramebuffer {
        return checkNull(this.gl.createFramebuffer());
    }

    bindArrayBuffer(buffer: WebGLBuffer) {
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, buffer);
    }

    bindFrameBuffer(frameBuffer: WebGLFramebuffer, width: number, height: number) {
        this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, frameBuffer);
        this.gl.viewport(0, 0, width, height);
        this.gl.scissor(0, 0, width, height);
    }

    useProgram(program: WebGLProgram) {
        this.gl.useProgram(program);
    }

    bindVertexArray(vao: WebGLVertexArray) {
        if (this.isWebGL2) {
            (this.gl as any).bindVertexArray(vao);
        } else {
            this.vao.bindVertexArrayOES(vao);
        }
    }

    deleteTexture(texture: WebGLTexture) {
        this.gl.deleteTexture(texture);
    }

    static initializeWebGL2Context(canvas: HTMLCanvasElement) {
        let gl: WebGLRenderingContext | null;

        gl = (canvas.getContext('webgl2')) as WebGLRenderingContext | null;

        if (!gl) return null;
        if (!gl.getExtension('EXT_color_buffer_float')) return null;
        if (isDebugMode() && !gl.getExtension('WEBGL_debug_renderer_info')) return null;

        return gl;
    }

    static initializeWebGL1Context(canvas: HTMLCanvasElement) {
        let gl: WebGLRenderingContext | null;
        let vao: any | null;

        gl = (canvas.getContext('webgl') || canvas.getContext('webgl-experimental')) as WebGLRenderingContext;

        if (!gl) return null;
        if (!gl.getExtension('OES_texture_float')) return null;
        if (!(vao = gl.getExtension('OES_vertex_array_object'))) return null;
        if (isDebugMode() && !gl.getExtension('WEBGL_debug_renderer_info')) return null;

        return {gl, vao};
    }

    static initializeContext() {
        let canvas = document.createElement('canvas');
        let gl: WebGLRenderingContext | null;
        let isWebGL2: boolean = false;
        let vao: any | null;

        gl = WebGLHandler.initializeWebGL2Context(canvas);
        if (gl) {
            isWebGL2 = true;
        } else {
            let res = WebGLHandler.initializeWebGL1Context(canvas);

            if (res) {
                gl = res.gl;
                vao = res.vao;
                isWebGL2 = false;
            } else {
                return null;
            }
        }

        gl.disable(gl.DEPTH_TEST);
        gl.disable(gl.STENCIL_TEST);
        gl.disable(gl.BLEND);
        gl.disable(gl.DITHER);
        gl.disable(gl.POLYGON_OFFSET_FILL);
        gl.disable(gl.SAMPLE_COVERAGE);
        gl.enable(gl.SCISSOR_TEST);
        gl.enable(gl.CULL_FACE);
        gl.cullFace(gl.BACK);

        return {gl, vao, isWebGL2};
    }

    /**
     * Check whether WebGL is supported or not
     * @protected
     */
    static checkAvailability() {
        if (availability === null) {
            if (!WebGLHandler.initializeContext()) {
                availability = false;
            } else {
                availability = true;
            }
        }

        return availability;
    }
}


let availability: boolean | null = null;

function checkNull<T>(obj: T | null) {
    if (obj === null) throw Error('Null is deteced');
    return obj as T;
}
