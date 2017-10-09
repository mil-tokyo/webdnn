/**
 * @module webdnn
 */
/** Don't Remove This comment block */
/// <reference path="./webgl2.d.ts" />

import { isDebugMode } from "./webdnn";

/**
 * @protected
 */
export function isWebGL2(gl: WebGLRenderingContext | WebGL2RenderingContext): gl is WebGL2RenderingContext {
    return gl.constructor.name === 'WebGL2RenderingContext'
}

/**
 * @protected
 */
export default class WebGLHandler {
    static IS_SAFARI = navigator.userAgent.toLowerCase().indexOf('safari') !== -1 && navigator.userAgent.toLowerCase().indexOf('chrome') === -1;
    readonly gl: WebGLRenderingContext | WebGL2RenderingContext;
    readonly vao: WebGLVertexArrayObjectExtension | null;

    constructor() {
        let {gl, vao} = checkNull(WebGLHandler.initializeContext());
        this.gl = gl;
        this.vao = vao;
    }

    createTexture(textureWidth: number, textureHeight: number, internalFormat: number, format: number) {
        let gl = this.gl;

        let texture = checkNull(gl.createTexture());

        gl.activeTexture(gl.TEXTURE0 + 9); // TODO: texture unit 9 is always available?
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, textureWidth, textureHeight, 0, format, gl.FLOAT, null);
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

    createVertexArray(): WebGLVertexArrayObject {
        if (isWebGL2(this.gl)) {
            return checkNull(this.gl.createVertexArray());
        } else {
            return checkNull(this.vao!.createVertexArrayOES());
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

    bindVertexArray(vao: WebGLVertexArrayObject) {
        if (isWebGL2(this.gl)) {
            this.gl.bindVertexArray(vao);
        } else {
            this.vao!.bindVertexArrayOES(vao);
        }
    }

    deleteTexture(texture: WebGLTexture) {
        this.gl.deleteTexture(texture);
    }

    static initializeWebGL2Context(canvas: HTMLCanvasElement = document.createElement('canvas')) {
        let gl: WebGLRenderingContext | null;

        gl = (canvas.getContext('webgl2')) as WebGL2RenderingContext | null;

        if (!gl) return null;
        if (!gl.getExtension('EXT_color_buffer_float')) return null;
        if (isDebugMode() && !gl.getExtension('WEBGL_debug_renderer_info')) return null;

        return gl;
    }

    static initializeWebGL1Context(canvas: HTMLCanvasElement = document.createElement('canvas')) {
        let gl: WebGLRenderingContext | null;
        let vao: WebGLVertexArrayObjectExtension | null;

        gl = (canvas.getContext('webgl') || canvas.getContext('webgl-experimental')) as WebGLRenderingContext | null;

        if (!gl) return null;
        if (!gl.getExtension('OES_texture_float')) return null;
        if (WebGLHandler.IS_SAFARI) {
            //TODO(Kiikurage)
            // Safari supports WebGL with OES_TEXTURE_FLOAT extension. However,
            // currently when WebGLRenderingContext#readPixels is called, an error is thrown.
            return null
        }

        if (!(vao = gl.getExtension('OES_vertex_array_object'))) return null;
        if (isDebugMode() && !gl.getExtension('WEBGL_debug_renderer_info')) return null;

        return {gl, vao};
    }

    static initializeContext() {
        let canvas = document.createElement('canvas');
        let gl: WebGLRenderingContext | null;
        let vao: WebGLVertexArrayObjectExtension | null = null;

        gl = WebGLHandler.initializeWebGL2Context(canvas);
        if (gl) {
            if (isDebugMode()) console.info('WebGL2 is enabled');

        } else {
            let res = WebGLHandler.initializeWebGL1Context(canvas);

            if (res) {
                gl = res.gl;
                vao = res.vao;
                if (isDebugMode()) console.info('WebGL2 is disabled');

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

        return {gl, vao};
    }

    /**
     * Check whether WebGL is supported or not
     * @protected
     */
    static checkAvailability() {
        if (availability === null) {
            let context = WebGLHandler.initializeContext();
            if (!context) {
                availability = false;

            } else if (context.gl.getParameter(context.gl.MAX_TEXTURE_SIZE) < 4096) {
                availability = false;

            } else {
                availability = true;
            }
        }

        return availability;
    }

    async waitForComplete() {
        let gl = this.gl;

        if (isWebGL2(gl)) {
            let sync = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0);
            let status = gl.clientWaitSync(sync, 0, 0);

            while (status !== gl.CONDITION_SATISFIED && status !== gl.ALREADY_SIGNALED) {
                await new Promise(r => setTimeout(r, 1));
                status = gl.clientWaitSync(sync, 0, 0);
            }

            gl.deleteSync(sync);
        } else {
            gl.finish();
        }
    }
}


let availability: boolean | null = null;

function checkNull<T>(obj: T | null) {
    if (obj === null) throw Error('Null is detected');
    return obj as T;
}
