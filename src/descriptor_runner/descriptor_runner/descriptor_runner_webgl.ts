/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import get_weight_decoder from "../decoder/get_weight_decoder";
import webdnnFetch, { readArrayBufferProgressively } from "../fetch";
import { GraphDescriptorWebGL } from "../graph_descriptor/graph_descriptor_webgl";
import { ResolvedAllocation } from "../graph_descriptor/memory_layout";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import { DEBUG } from "../webdnn";
import { DescriptorRunner } from "./descriptor_runner";

/**
 * @protected
 */
interface RuntimeProgramInfo {
    program: WebGLProgram,
    frameBuffer,
    width: number,
    height: number,
    inputs: {
        buffer: WebGLBuffer,
        uniformIndex: number
    }[],
    uniforms: {
        func: (...args: any[]) => void,
        args: any[]
    }[],
    attributes: {
        loc: number,
        size: number,
        stride: number,
        offset: number
    }[],
    output: WebGLBuffer
}

/**
 * @protected
 */
interface RuntimeInfo {
    inputs: WebGLBuffer[],
    outputs: WebGLBuffer[]
    programs: RuntimeProgramInfo[]
}

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
 * Channel usage for WebGLBuffer
 * @protected
 */
enum ChannelMode {R, RGBA}

/**
 * Buffer wrapper for WebGL backend
 * @TODO: Move this into `/buffer/buffer_webgl.ts` and implement `Buffer` interface.
 * @protected
 */
class WebGLBuffer {
    private gl: WebGLRenderingContext;
    readonly channelMode: ChannelMode = ChannelMode.RGBA;
    readonly elementsPerPixel: number;
    readonly length: number;
    readonly array: Float32Array;
    readonly textureWidth: number;
    readonly textureHeight: number;
    private texture: WebGLTexture;

    constructor(gl: WebGLRenderingContext, length: number,
                array: Float32Array | null = null,
                channelMode: ChannelMode = ChannelMode.R) {
        this.gl = gl;
        this.channelMode = channelMode;
        switch (this.channelMode) {
            case ChannelMode.RGBA:
                this.elementsPerPixel = 4;
                break;

            case ChannelMode.R:
                this.elementsPerPixel = 1;
                break;

            default:
                throw Error('Unknown channel mode');
        }

        this.length = length;
        this.array = array || new Float32Array(this.length);

        // width is fixed as 1024, height is flexible.
        // FIXME: flexible width for efficient memory allocation
        const packedLength = Math.ceil(length / this.elementsPerPixel);
        this.textureWidth = packedLength <= 2048 ? packedLength : 2048;
        this.textureHeight = Math.ceil(packedLength / 2048);

        let texture = checkNull(gl.createTexture());
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, this.textureWidth, this.textureHeight, 0, gl.RGBA, gl.FLOAT, null);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        this.texture = texture;

        if (array) this.uploadToGPU();
    }

    uploadToGPU() {
        let gl = this.gl;

        let tmp = this.pack(this.array);
        if (tmp.length != this.textureWidth * this.textureHeight * 4) {
            let tmp2 = new Float32Array(this.textureWidth * this.textureHeight * 4);
            tmp2.set(tmp, 0);
            tmp = tmp2;
        }

        gl.bindTexture(gl.TEXTURE_2D, this.texture);
        gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, this.textureWidth, this.textureHeight, gl.RGBA, gl.FLOAT, tmp);
    }

    downloadToCPU() {
        let gl = this.gl;
        let tmp = new Float32Array(this.textureWidth * this.textureHeight * 4);

        gl.bindTexture(gl.TEXTURE_2D, this.texture);
        gl.readPixels(0, 0, this.textureWidth, this.textureHeight, gl.RGBA, gl.FLOAT, tmp);

        this.array.set(this.unpack(tmp).slice(0, this.length), 0);
    }

    bindTextureToUnit(unit: number) {
        let gl = this.gl;

        gl.activeTexture(gl.TEXTURE0 + unit);
        gl.bindTexture(gl.TEXTURE_2D, this.texture);
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.texture, 0);
    }

    private pack(array: Float32Array) {
        switch (this.channelMode) {
            case ChannelMode.RGBA:
                return new Float32Array(array);

            case ChannelMode.R:
                let result = new Float32Array(array.length * 4);
                for (let i = 0; i < array.length; i++) result[i * 4] = array[i];
                return result;

            default:
                throw Error('Unknown channel mode');
        }
    }

    private unpack(array: Float32Array) {
        switch (this.channelMode) {
            case ChannelMode.RGBA:
                return new Float32Array(array);

            case ChannelMode.R:
                let result = new Float32Array(array.length / 4);
                for (let i = 0; i < array.length / 4; i++) result[i] = array[i * 4];
                return result;

            default:
                throw Error('Unknown channel mode');
        }
    }
}

/**
 * @protected
 */
export default class DescriptorRunnerWebGL extends DescriptorRunner<GraphDescriptorWebGL> {
    readonly backendName = 'webgl';

    private runtimeInfo: RuntimeInfo;
    private gl: WebGLRenderingContext;
    private vertexShader: WebGLShader;
    private programs: Map<string, WebGLProgram>;
    private buffers: Map<string, WebGLBuffer>;

    private inputViews: SymbolicFloat32Array[] | null;
    private outputViews: SymbolicFloat32Array[] | null;

    static checkAvailability() {
        return IS_WEBGL_SUPPORTED;
    }

    async init() {
        this.gl = initializeWebGLRenderingContext()!;
        let vertexBuffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, vertexBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, vertexArray, this.gl.STATIC_DRAW);
        this.buffers = new Map();
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
        let buffers = this.buffers;

        Object.entries(descriptor.memory_layout.static.allocations)
            .forEach(([name, allocation]: [string, ResolvedAllocation]) => {
                let array = (allocation.offset + allocation.size <= weight.length) ?
                    new Float32Array(weight.buffer, 4 * allocation.offset, allocation.size) :
                    null;

                let buffer = new WebGLBuffer(this.gl, allocation.size, array);
                buffers.set(name, buffer);
            });

        (await this.getInputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(view.name)!.array.buffer));

        (await this.getOutputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(view.name)!.array.buffer));
    }

    private async initializeDynamicBuffer() {
        if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
        if (!this.placeholderContext) throw Error("PlaceholderContext is not initialized.");
        let descriptor = this.descriptor;

        let placeholderContext = this.placeholderContext;
        let buffers = this.buffers;

        Object.entries(descriptor.memory_layout.dynamic.allocations)
            .forEach(([name, allocation]: [string, ResolvedAllocation]) => {
                let buffer = new WebGLBuffer(this.gl, placeholderContext.resolve(allocation.size));
                buffers.set(name, buffer);
            });

        (await this.getInputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(view.name)!.array.buffer));

        (await this.getOutputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(view.name)!.array.buffer));

        this.buildPipeline();
    }

    private async setDescriptor(descriptor: GraphDescriptorWebGL) {
        this.descriptor = descriptor;

        //reset all datum depend on old descriptor
        this.placeholderContext = new PlaceholderContext(descriptor.placeholders);
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
        // TODO:
        if (Object.keys(this.descriptor.placeholders).length > 0) throw Error('Currently, WebGL backend doesn\'t support Placeholder feature.')
    }

    getInputViews() {
        if (this.inputViews) return this.inputViews;

        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');

        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;

        this.inputViews = descriptor.inputs.map(name => {
            let allocation = descriptor.memory_layout.static.allocations[name] || descriptor.memory_layout.dynamic.allocations[name];
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

    private buildPipeline() {
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');
        if (!this.placeholderContext.isResolved) throw new Error(`Not all placeholders are resolved: ${this.placeholderContext}`);

        let gl = this.gl;
        let buffers = this.buffers;

        this.runtimeInfo = {
            inputs: this.getInputViews().map(view => buffers.get(view.name)!),
            outputs: this.getOutputViews().map(view => buffers.get(view.name)!),
            programs: this.descriptor.exec_infos.map(execInfo => {

                // frame buffer
                let frameBuffer = gl.createFramebuffer()!;

                // inputs
                let inputs = execInfo.inputs.map(input => ({
                    buffer: buffers.get(input.variable_name)!,
                    uniformIndex: 1 + input.value
                }));

                //output
                let output = buffers.get(execInfo.output)!;

                // shader
                let program = this.programs.get(execInfo.shader_name)!;
                gl.useProgram(program);

                // uniforms
                let uniforms = Object.keys(execInfo.uniforms).map(name => {
                    let {type, value} = execInfo.uniforms[name];
                    switch (type) {
                        case 'int':
                            return {
                                func: gl.uniform1i,
                                args: [gl.getUniformLocation(program, name), value]
                            };

                        case 'float':
                            return {
                                func: gl.uniform1f,
                                args: [gl.getUniformLocation(program, name), value]
                            };

                        case 'vec2':
                            return {
                                func: gl.uniform2fv,
                                args: [gl.getUniformLocation(program, name), value]
                            };

                        case 'vec4':
                            return {
                                func: gl.uniform4fv,
                                args: [gl.getUniformLocation(program, name), value]
                            };

                        case 'sampler2D':
                            // Bind input as unit "1", "2", ... . Unit "0" is reserved for output.
                            return {
                                func: gl.uniform1i,
                                args: [gl.getUniformLocation(program, name), 1 + value]
                            };

                        default:
                            throw TypeError(`Incompatible type for uniform parameter: ${type}`);
                    }
                });

                // attributes
                let attributes = [{
                    loc: gl.getAttribLocation(program, '_xy'),
                    size: 2,
                    stride: 0,
                    offset: 0
                }];

                // run
                return {
                    program: program,
                    frameBuffer: frameBuffer,
                    width: output.textureWidth,
                    height: output.textureHeight,
                    inputs: inputs,
                    output: output,
                    uniforms: uniforms,
                    attributes: attributes
                };
            })
        };
    }

    async run(): Promise<void> {
        if (this._running) throw new Error('Calling another run() while running.');
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');
        if (!this.placeholderContext.isResolved) throw new Error(`Not all placeholders are resolved: ${this.placeholderContext}`);

        let gl = this.gl;
        let runtimeInfo = this.runtimeInfo;
        this._running = true;

        //Upload all input values to GPU
        for (let buffer of runtimeInfo.inputs) buffer.uploadToGPU();

        for (let runtimeProgramInfo of runtimeInfo.programs) {
            gl.viewport(0, 0, runtimeProgramInfo.width, runtimeProgramInfo.height);

            // frameBuffer
            gl.bindFramebuffer(gl.FRAMEBUFFER, runtimeProgramInfo.frameBuffer);

            // inputs
            for (let {buffer, uniformIndex} of runtimeProgramInfo.inputs) buffer.bindTextureToUnit(uniformIndex);

            // output
            runtimeProgramInfo.output.bindTextureToUnit(0);

            // shader
            gl.useProgram(runtimeProgramInfo.program);

            // uniforms
            for (let uniform of runtimeProgramInfo.uniforms) uniform.func.apply(gl, uniform.args);

            // attributes
            for (let attribute of runtimeProgramInfo.attributes) {
                gl.enableVertexAttribArray(attribute.loc);
                gl.vertexAttribPointer(attribute.loc, attribute.size, gl.FLOAT, false, attribute.stride, attribute.offset);
            }

            // run
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexArray.length / 2);
        }

        //Download all output values to CPU
        for (let buffer of runtimeInfo.outputs) buffer.downloadToCPU();

        this._running = false;
    }
}

function initializeWebGLRenderingContext() {
    let canvas = document.createElement('canvas');
    let gl = (canvas.getContext('webgl') || canvas.getContext('webgl-experimental')) as WebGLRenderingContext;
    if (!gl) return null;

    if (!gl.getExtension('OES_texture_float')) return null;
    if (DEBUG && !gl.getExtension('WEBGL_debug_renderer_info')) return null;

    return gl;
}

function checkNull<T>(v: T | null | undefined): T {
    if (!v) throw Error('null error');
    return v;
}

let IS_WEBGL_SUPPORTED: boolean = false;

document.addEventListener('DOMContentLoaded', () => IS_WEBGL_SUPPORTED = !!initializeWebGLRenderingContext());
