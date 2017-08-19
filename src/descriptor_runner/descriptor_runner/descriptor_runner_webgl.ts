/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import get_weight_decoder from "../decoder/get_weight_decoder";
import webdnnFetch, { readArrayBufferProgressively } from "../fetch";
import { GraphDescriptorWebGL, GraphDescriptorWebGLExecInfos } from "../graph_descriptor/graph_descriptor_webgl";
import { ResolvedAllocation } from "../graph_descriptor/memory_layout";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import { DescriptorRunner } from "./descriptor_runner";


// [x y z] * [upper-left, lower-left, upper-right, lower-right]
/**
 * @protected
 */
const vertexArray = new Float32Array([
    -1, +1,
    -1, -1,
    +1, +1,
    +1, -1
]);

/**
 * @protected
 */
export default class DescriptorRunnerWebGL extends DescriptorRunner<GraphDescriptorWebGL> {
    readonly backendName = 'webgl';

    private gl: WebGLRenderingContext;
    private vertexShader: WebGLShader;
    private programs: Map<string, WebGLProgram>;
    private textures: Map<string, WebGLTexture>;

    private inputViews: SymbolicFloat32Array[] | null;
    private outputViews: SymbolicFloat32Array[] | null;

    private executionInfos: GraphDescriptorWebGLExecInfos[] | null;

    static checkAvailability() {
        return IS_WEBGL_SUPPORTED;
    }

    async init() {
        this.gl = initializeWebGLRenderingContext()!;
        let vertexBuffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, vertexBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, vertexArray, this.gl.STATIC_DRAW);
        this.textures = new Map();
    }

    async load(directory: string, progressCallback?: (loaded: number, total: number) => any) {
        let [descriptor, weightRawArray] = await Promise.all([
            webdnnFetch(`${directory}/graph_${this.backendName}.json`, {ignoreCache: this.ignoreCache})
                .then(res => res.json() as Promise<GraphDescriptorWebGL>),

            webdnnFetch(`${directory}/weight_${this.backendName}.bin`, {ignoreCache: this.ignoreCache})
                .then(res => readArrayBufferProgressively(res, progressCallback))
        ]);

        await this.setDescriptor(descriptor);
        await this.compile();

        await this.initializeStaticBuffer(weightRawArray);
        if (this.placeholderContext && this.placeholderContext.isResolved) await this.initializeDynamicBuffer();
    }

    private async initializeStaticBuffer(weightRawArray: ArrayBuffer) {
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        let descriptor = this.descriptor;

        let decoder = get_weight_decoder(this.descriptor.weight_encoding);
        let weight = await decoder.decode(new Uint8Array(weightRawArray), this.descriptor.memory_layout);
        let textures = this.textures;

        Object.entries(descriptor.memory_layout.static.allocations)
            .forEach(([name, allocation]: [string, ResolvedAllocation]) => {
                let value = allocation.offset + allocation.size <= weight.length ?
                    packToRGBA(new Float32Array(weight.buffer, 4 * allocation.offset, allocation.size)) :
                    null;

                let texture = createTextureBuffer(this.gl, allocation.size, 1, value);
                textures.set(name, texture);
            });

        (await this.getInputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer((new Float32Array(view.length)).buffer));

        (await this.getOutputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer((new Float32Array(view.length)).buffer));
    }

    private async initializeDynamicBuffer() {
        if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
        if (!this.placeholderContext) throw Error("PlaceholderContext is not initialized.");
        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;
        let textures = this.textures;

        Object.entries(descriptor.memory_layout.dynamic.allocations)
            .forEach(([name, allocation]: [string, ResolvedAllocation]) => {
                let texture = createTextureBuffer(this.gl, placeholderContext.resolve(allocation.size), 1);

                textures.set(name, texture);
            });

        (await this.getInputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer((new Float32Array(placeholderContext.resolve(view.length))).buffer));

        (await this.getOutputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer((new Float32Array(placeholderContext.resolve(view.length))).buffer));
    }

    private async setDescriptor(descriptor: GraphDescriptorWebGL) {
        this.descriptor = descriptor;

        //reset all datum depend on old descriptor
        this.placeholderContext = new PlaceholderContext(descriptor.placeholders);
        this.executionInfos = descriptor.exec_infos;
    }

    private async compile() {
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        let descriptor = this.descriptor;

        this.programs = new Map();
        this.vertexShader = checkNull(this.gl.createShader(this.gl.VERTEX_SHADER));
        this.gl.shaderSource(this.vertexShader, `
            precision highp float;
            attribute vec2 _xy;
            void main() { 
              gl_Position = vec4(_xy, 0, 1); 
            }
        `);
        this.gl.compileShader(this.vertexShader);
        if (!this.gl.getShaderParameter(this.vertexShader, this.gl.COMPILE_STATUS)) {
            console.error(this.gl.getShaderInfoLog(this.vertexShader));
            throw Error("Shader Compile failed: " + this.gl.getShaderInfoLog(this.vertexShader));
        }

        Object.keys(descriptor.shader_sources)
            .forEach(name => {
                let shader = checkNull(this.gl.createShader(this.gl.FRAGMENT_SHADER));
                this.gl.shaderSource(shader, descriptor.shader_sources[name]);
                this.gl.compileShader(shader);
                if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
                    console.error(this.gl.getShaderInfoLog(shader));
                    throw Error("Shader Compile failed: " + this.gl.getShaderInfoLog(shader));
                }

                let program = checkNull(this.gl.createProgram());
                this.gl.attachShader(program, shader);
                this.gl.attachShader(program, this.vertexShader);
                this.gl.linkProgram(program);
                if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
                    console.error(this.gl.getProgramInfoLog(program));
                    throw Error('ShaderProgram Initialization failed.');
                }

                this.programs.set(name, program);
            });
    }

    async setPlaceholderValue(values: { [key: string]: number }) {
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized.');
        let placeholderContext = this.placeholderContext;

        placeholderContext.update(values);
        if (!placeholderContext.isResolved) return;

        if (!this.descriptor) throw new Error('Descriptor is not loaded');

        await this.initializeDynamicBuffer();

        // resolve placeholders in execution info
        // TODO: あとで
    }

    getInputViews() {
        if (this.inputViews) return this.inputViews;

        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');

        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;

        this.inputViews = descriptor.inputs.map(name => {
            let allocation = descriptor.memory_layout.static.allocations[name] || descriptor.memory_layout.dynamic.allocations[name];
            allocation.offset = 0; // FIXME なんかきもい
            let view = new SymbolicFloat32Array(allocation, placeholderContext, true);

            return view;
        });

        return this.inputViews;
    }

    getOutputViews() {
        if (this.outputViews) return this.outputViews;

        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');

        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;

        this.outputViews = descriptor.outputs.map(name => {
            let allocation = descriptor.memory_layout.static.allocations[name] || descriptor.memory_layout.dynamic.allocations[name];
            let view = new SymbolicFloat32Array(allocation, placeholderContext, true);

            return view;
        });

        return this.outputViews;
    }

    async run(): Promise<void> {
        if (this._running) throw new Error('Calling another run() while running.');
        if (!this.executionInfos) throw new Error('ExecutionInfos is not loaded');
        if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');
        if (!this.placeholderContext.isResolved) throw new Error(`Not all placeholders are resolved: ${this.placeholderContext}`);

        let gl = this.gl;
        let textures = this.textures;

        //Upload all input values to GPU
        for (let view of this.getInputViews()) {
            let texture = checkNull(textures.get(view.name));
            let array = view.toActual();
            gl.bindTexture(gl.TEXTURE_2D, texture);
            gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, array.length, 1, gl.RGBA, gl.FLOAT, packToRGBA(array));
        }

        this._running = true;
        for (let i = 0; i < this.executionInfos.length; i++) {
            let execInfo = this.executionInfos[i];
            const width = execInfo.width;
            const height = 1;

            gl.viewport(0, 0, width, height);
            gl.scissor(0, 0, width, height);

            // frameBuffer
            let frameBuffer = gl.createFramebuffer();
            gl.bindFramebuffer(gl.FRAMEBUFFER, frameBuffer);

            // shader
            let program = checkNull(this.programs.get(execInfo.shader_name));
            gl.useProgram(program);

            // inputs
            execInfo.inputs.forEach((input, i) => {
                let texture = checkNull(textures.get(input.variable_name));
                gl.activeTexture(gl.TEXTURE1 + i); // Bind input as unit "1", "2", ... . Unit "0" is reserved for output.
                gl.bindTexture(gl.TEXTURE_2D, texture);
                gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);
            });

            // output
            let texture = checkNull(textures.get(execInfo.output));
            gl.activeTexture(gl.TEXTURE0 + 0); // Bind output as slot "0"
            gl.bindTexture(gl.TEXTURE_2D, texture);
            gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);

            // uniforms
            let uniforms = execInfo.uniforms;
            Object.keys(uniforms).forEach(name => {
                let {type, value} = uniforms[name];
                switch (type) {
                    case 'int':
                        gl.uniform1i(gl.getUniformLocation(program, name), value);
                        break;

                    case 'float':
                        gl.uniform1f(gl.getUniformLocation(program, name), value);
                        break;

                    case 'sampler2D':
                        // Bind input as unit "1", "2", ... . Unit "0" is reserved for output.
                        gl.uniform1i(gl.getUniformLocation(program, name), 1 + value);
                        break;

                    default:
                        throw TypeError(`Incompatible type for uniform parameter: ${type}`);
                }
            });

            // attributes
            let loc = gl.getAttribLocation(program, '_xy');
            gl.enableVertexAttribArray(loc);
            gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

            // run
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexArray.length / 2);
        }
        gl.flush();

        //Download all output values to CPU
        for (let view of this.getOutputViews()) {
            let texture = checkNull(textures.get(view.name));
            let array = view.toActual();
            let tmp = new Float32Array(array.length * 4);
            gl.bindTexture(gl.TEXTURE_2D, texture);
            gl.readPixels(0, 0, array.length, 1, gl.RGBA, gl.FLOAT, tmp);
            view.setArrayBuffer(unpackFromRGBA(tmp));
        }

        this._running = false;
    }
}

function packToRGBA(array: Float32Array) {
    let result = new Float32Array(array.length * 4);
    for (let i = 0; i < array.length; i++) result[i * 4] = array[i];
    return result;
}

function unpackFromRGBA(array: Float32Array) {
    let result = new Float32Array(array.length / 4);
    for (let i = 0; i < result.length; i++) result[i] = array[i * 4];
    return result;
}

function createTextureBuffer(gl: WebGLRenderingContext, width: number, height: number, value: Float32Array | null = null) {
    let texture = checkNull(gl.createTexture());
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.FLOAT, value);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    return texture;
}

function initializeWebGLRenderingContext() {
    let canvas = document.createElement('canvas');
    let gl = (canvas.getContext('webgl') || canvas.getContext('webgl-experimental')) as WebGLRenderingContext;
    if (!gl) return null;

    let ext = gl.getExtension('OES_texture_float');
    if (!ext) return null;

    return gl;
}

function checkNull<T>(v: T | null | undefined): T {
    if (!v) throw Error('null error');
    return v;
}

let IS_WEBGL_SUPPORTED: boolean = false;

document.addEventListener('DOMContentLoaded', () => {
    IS_WEBGL_SUPPORTED = !!initializeWebGLRenderingContext();
});
