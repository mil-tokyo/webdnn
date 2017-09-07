/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { isDebugMode } from "./webdnn";

export declare interface WebGLVertexArrayObject {
}

/**
 * @protected
 */
export default class WebGLHandler {
    readonly gl: WebGLRenderingContext;
    readonly vao: any;

    constructor() {
        let {gl, vao} = checkNull(WebGLHandler.initializeContext());
        this.gl = gl;
        this.vao = vao;
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

    createVertexArrayObject(): WebGLVertexArrayObject {
        return checkNull(this.vao.createVertexArrayOES() as WebGLVertexArrayObject | null);
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
        this.vao.bindVertexArrayOES(vao);
    }

    static initializeContext() {
        let canvas = document.createElement('canvas');
        let gl = (canvas.getContext('webgl') || canvas.getContext('webgl-experimental')) as WebGLRenderingContext;
        if (!gl) return null;

        let vao;
        if (!gl.getExtension('OES_texture_float')) return null;
        if (!(vao = gl.getExtension('OES_vertex_array_object'))) return null;
        if (isDebugMode() && !gl.getExtension('WEBGL_debug_renderer_info')) return null;

        gl.disable(gl.DEPTH_TEST);
        gl.disable(gl.STENCIL_TEST);
        gl.disable(gl.BLEND);
        gl.disable(gl.DITHER);
        gl.disable(gl.POLYGON_OFFSET_FILL);
        gl.disable(gl.SAMPLE_COVERAGE);
        gl.enable(gl.SCISSOR_TEST);
        gl.enable(gl.CULL_FACE);
        gl.cullFace(gl.BACK);

        return {
            gl: gl,
            vao: vao
        };
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
