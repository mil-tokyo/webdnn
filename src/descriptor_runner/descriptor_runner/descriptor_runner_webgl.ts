/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import get_weight_decoder from "../decoder/get_weight_decoder";
import webdnnFetch, { readArrayBufferProgressively } from "../fetch";
import { ChannelMode, GraphDescriptorWebGL } from "../graph_descriptor/graph_descriptor_webgl";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import { isDebugMode } from "../webdnn";
import { DescriptorRunner } from "./descriptor_runner";

/**
 * @protected
 */
interface RuntimeProgramInfo {
    program: WebGLProgram,
    frameBuffer: WebGLFramebuffer,
    name: string,
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
    vao: any,
    output: WebGLBuffer,
    disposable: WebGLBuffer[]
}

/**
 * @protected
 */
interface RuntimeInfo {
    inputs: WebGLBuffer[],
    outputs: WebGLBuffer[]
    programs: RuntimeProgramInfo[]
}

// [x y u v] * [upper-left, lower-left, upper-right, lower-right]
/**
 * @protected
 */
const vertexArray = new Float32Array([
    -1, +1,
    -1, -1,
    +1, +1,
    +1, -1,
]);

/**
 * Buffer wrapper for WebGL backend
 * @TODO: Move this into `/buffer/buffer_webgl.ts` and implement `Buffer` interface.
 * @protected
 */
class WebGLBuffer {
    private gl: WebGLRenderingContext;
    readonly channelMode: ChannelMode;
    readonly elementsPerPixel: number;
    readonly length: number;
    readonly array: Float32Array;
    readonly textureWidth: number;
    readonly textureHeight: number;
    private _texture: WebGLTexture | null = null;
    readonly name: string;
    private textureUnit: number = -1;

    get texture() {
        return this._texture;
    }

    constructor(gl: WebGLRenderingContext, length: number, name: string, array: Float32Array | null, channelMode: ChannelMode) {
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

        this.length = length;
        this.array = array || new Float32Array(this.length);

        // width is fixed as 1024, height is flexible.
        // FIXME: flexible width for efficient memory allocation
        const packedLength = Math.ceil(length / this.elementsPerPixel);
        this.textureWidth = packedLength <= 2048 ? packedLength : 2048;
        this.textureHeight = Math.ceil(packedLength / 2048);
    }

    private initializeTexture() {
        let gl = this.gl;
        let texture = checkNull(gl.createTexture());
        gl.activeTexture(gl.TEXTURE0 + 9); // TODO
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, this.textureWidth, this.textureHeight, 0, gl.RGBA, gl.FLOAT, null);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.bindTexture(gl.TEXTURE_2D, null);
        this._texture = texture;
    }

    private disposeTexture() {
        this.unbindTextureFromUnit();
        this.gl.deleteTexture(this.texture);
        this._texture = null;
    }

    allocateOnGPU() {
        if (!this.texture) this.initializeTexture();
    }

    uploadToGPU() {
        this.allocateOnGPU();
        let gl = this.gl;

        let tmp = this.pack(this.array);
        if (tmp.length != this.textureWidth * this.textureHeight * 4) {
            let tmp2 = new Float32Array(this.textureWidth * this.textureHeight * 4);
            tmp2.set(tmp, 0);
            tmp = tmp2;
        }

        gl.activeTexture(gl.TEXTURE0 + 9); // TODO
        gl.bindTexture(gl.TEXTURE_2D, this.texture);
        gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, this.textureWidth, this.textureHeight, gl.RGBA, gl.FLOAT, tmp);
        gl.bindTexture(gl.TEXTURE_2D, null);
    }

    downloadToCPU() {
        let gl = this.gl;
        let tmp = new Float32Array(this.textureWidth * this.textureHeight * 4);

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.texture, 0);
        gl.readPixels(0, 0, this.textureWidth, this.textureHeight, gl.RGBA, gl.FLOAT, tmp);
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, null, 0);

        this.array.set(this.unpack(tmp).slice(0, this.length), 0);
        this.disposeTexture();
    }

    releaseGPUMemory() {
        this.disposeTexture();
    }

    bindTextureToUnit(unit: number) {
        if (!this.texture) this.uploadToGPU();
        let gl = this.gl;

        this.textureUnit = unit;
        gl.activeTexture(gl.TEXTURE0 + this.textureUnit);
        gl.bindTexture(gl.TEXTURE_2D, this.texture);
    }

    unbindTextureFromUnit() {
        if (this.textureUnit === -1) return;
        let gl = this.gl;

        gl.activeTexture(gl.TEXTURE0 + this.textureUnit);
        gl.bindTexture(gl.TEXTURE_2D, null);
        this.textureUnit = -1;
    }

    bindTextureToCurrentFrameBuffer() {
        if (this.textureUnit !== -1) throw ('This buffer is already registered as input texture. Please unbind first.');
        if (!this.texture) this.allocateOnGPU();
        let gl = this.gl;

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.texture, 0);
    }

    unbindTextureFromCurrentFrameBuffer() {
        let gl = this.gl;

        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, null, 0);
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
    private extensions: { vao: any };

    static checkAvailability() {
        //TODO(Kiikurage)
        // Safari supports WebGL with OES_TEXTURE_FLOAT extension. However,
        // currently when WebGLRenderingContext#readPixels is called, an error is thrown.
        const IS_SAFARI = navigator.userAgent.toLowerCase().indexOf('safari') !== -1 &&
            navigator.userAgent.toLowerCase().indexOf('chrome') === -1;
        return IS_WEBGL_SUPPORTED && !IS_SAFARI;
    }

    async init() {
        if (!DescriptorRunnerWebGL.checkAvailability()) throw Error('WebGL backend is not supported in this browser.');

        let {gl, extensions} = initializeWebGLRenderingContext()!;
        this.gl = gl;
        this.extensions = extensions;
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
        let weight = await decoder.decode(new Uint8Array(weightRawArray));
        let buffers = this.buffers;

        Object.entries(descriptor.allocations)
            .forEach(([name, {allocation_size, channel_mode}]) => {
                buffers.set(name, new WebGLBuffer(this.gl, allocation_size, name, null, channel_mode));
            });

        Object.entries(descriptor.constants_map)
            .forEach(([variable_name, {size, byte_offset}]) => {
                let buffer = buffers.get(descriptor.variables[variable_name].allocation_name)!;
                buffer.array.set(new Float32Array(weight.buffer, byte_offset, size));
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

        Object.entries(descriptor.allocations)
            .forEach(([name, {allocation_size, channel_mode}]) => {
                if (typeof allocation_size == 'number') return;

                buffers.set(name, new WebGLBuffer(this.gl, placeholderContext.resolve(allocation_size), name, null, channel_mode));
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
            let {variable_size, allocation_name} = descriptor.variables[name];
            let view = new SymbolicFloat32Array({
                name: allocation_name,
                size: variable_size,
                offset: 0
            }, placeholderContext, true);

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
            let {variable_size, allocation_name} = descriptor.variables[name];
            let view = new SymbolicFloat32Array({
                name: allocation_name,
                size: variable_size,
                offset: 0
            }, placeholderContext, true);

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
        let descriptor = this.descriptor;
        let referenceCount = new Map<WebGLBuffer, number>();

        this.runtimeInfo = {
            inputs: this.getInputViews().map(view => buffers.get(view.name)!),
            outputs: this.getOutputViews().map(view => buffers.get(view.name)!),
            programs: this.descriptor.exec_infos.map(execInfo => {
                // inputs
                let inputs = execInfo.inputs.map(input => {
                    let buffer = buffers.get(descriptor.variables[input.variable_name].allocation_name)!;

                    if (!referenceCount.has(buffer)) referenceCount.set(buffer, 0);
                    referenceCount.set(buffer, referenceCount.get(buffer)! + 1);

                    return {
                        buffer: buffer,
                        uniformIndex: input.value
                    }
                });

                //output
                let output = buffers.get(descriptor.variables[execInfo.output].allocation_name)!;

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
                            return {
                                func: gl.uniform1i,
                                args: [gl.getUniformLocation(program, name), value]
                            };

                        default:
                            throw TypeError(`Incompatible type for uniform parameter: ${type}`);
                    }
                });

                // vao
                let vao = this.extensions.vao.createVertexArrayOES();
                this.extensions.vao.bindVertexArrayOES(vao);

                // attributes
                let loc = gl.getAttribLocation(program, '_xy');
                gl.vertexAttribPointer(loc, 2, gl.FLOAT, true, 8, 0);
                gl.enableVertexAttribArray(loc);

                // run
                return {
                    program: program,
                    frameBuffer: gl.createFramebuffer()!,
                    name: execInfo.shader_name,
                    width: output.textureWidth,
                    height: output.textureHeight,
                    inputs: inputs,
                    output: output,
                    vao: vao,
                    uniforms: uniforms,
                    disposable: []
                };
            })
        };

        for (let runtimeProgramInfo of this.runtimeInfo.programs) {
            runtimeProgramInfo.inputs.forEach(({buffer}) => {
                let count = referenceCount.get(buffer)! - 1;
                if (count == 0) {
                    runtimeProgramInfo.disposable.push(buffer);
                }
                referenceCount.set(buffer, count);
            });
        }
    }

    async run(): Promise<void> {
        if (this._running) throw new Error('Calling another run() while running.');
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');
        if (!this.placeholderContext.isResolved) throw new Error(`Not all placeholders are resolved: ${this.placeholderContext}`);
        this._running = true;

        let gl = this.gl;
        let runtimeInfo = this.runtimeInfo;
        let vaoExtension = this.extensions.vao;

        //Upload all input values to GPU
        for (let buffer of runtimeInfo.inputs) buffer.uploadToGPU();

        if (isDebugMode()) {
            let records: any = [];
            let totalElapsedTime = 0;

            for (let runtimeProgramInfo of runtimeInfo.programs) {
                let start = performance.now();

                //vao
                vaoExtension.bindVertexArrayOES(runtimeProgramInfo.vao);

                // frameBuffer
                gl.bindFramebuffer(gl.FRAMEBUFFER, runtimeProgramInfo.frameBuffer);
                gl.viewport(0, 0, runtimeProgramInfo.width, runtimeProgramInfo.height);
                gl.scissor(0, 0, runtimeProgramInfo.width, runtimeProgramInfo.height);

                // inputs
                for (let {buffer, uniformIndex} of runtimeProgramInfo.inputs) {
                    gl.activeTexture(gl.TEXTURE0 + uniformIndex);
                    gl.bindTexture(gl.TEXTURE_2D, buffer.texture);
                }

                // output
                gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, runtimeProgramInfo.output.texture, 0);

                // shader
                gl.useProgram(runtimeProgramInfo.program);

                // uniforms
                for (let uniform of runtimeProgramInfo.uniforms) uniform.func.apply(gl, uniform.args);

                // run
                gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexArray.length / 2);
                gl.finish();
                let elapsedTime = performance.now() - start;
                records.push({
                    'Kernel': runtimeProgramInfo.name,
                    'Elapsed time [ms]': elapsedTime
                });
                totalElapsedTime += elapsedTime;

                for (let {buffer, uniformIndex} of runtimeProgramInfo.inputs) {
                    buffer.downloadToCPU();
                    console.log(uniformIndex, buffer.array);
                }

                runtimeProgramInfo.output.downloadToCPU();
                console.log(runtimeProgramInfo.name, runtimeProgramInfo.output.array);
            }

            let summary = Array.from(Object.values(records.reduce((summary, record) => {
                if (!(record['Kernel'] in summary)) {
                    summary[record['Kernel']] = {
                        'Kernel': record['Kernel'],
                        'Count': 0,
                        'Elapsed time [ms]': 0,
                    };
                }

                summary[record['Kernel']]['Count']++;
                summary[record['Kernel']]['Elapsed time [ms]'] += record['Elapsed time [ms]'];

                return summary;
            }, {})));
            summary.forEach(record => record['Ratio [%]'] = (record['Elapsed time [ms]'] / totalElapsedTime).toFixed(2));

            console.table(records);
            console.table(summary);

        } else {
            for (let runtimeProgramInfo of runtimeInfo.programs) {
                //vao
                vaoExtension.bindVertexArrayOES(runtimeProgramInfo.vao);

                // frameBuffer
                gl.bindFramebuffer(gl.FRAMEBUFFER, runtimeProgramInfo.frameBuffer);
                gl.viewport(0, 0, runtimeProgramInfo.width, runtimeProgramInfo.height);
                gl.scissor(0, 0, runtimeProgramInfo.width, runtimeProgramInfo.height);

                // inputs
                for (let {buffer, uniformIndex} of runtimeProgramInfo.inputs) {
                    buffer.bindTextureToUnit(uniformIndex);
                }

                // output
                runtimeProgramInfo.output.bindTextureToCurrentFrameBuffer();

                // shader
                gl.useProgram(runtimeProgramInfo.program);

                // uniforms
                for (let uniform of runtimeProgramInfo.uniforms) uniform.func.apply(gl, uniform.args);

                // run
                gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexArray.length / 2);

                // release buffers
                for (let buffer of runtimeProgramInfo.disposable) buffer.releaseGPUMemory();
                // runtimeProgramInfo.output.downloadToCPU();
            }
        }

        for (let buffer of runtimeInfo.outputs) buffer.downloadToCPU();

        this._running = false;
    }
}

function initializeWebGLRenderingContext() {
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
        extensions: {
            vao: vao
        }
    };
}

function checkBrowserSupportStatus() {
    if (!initializeWebGLRenderingContext()) return;

    IS_WEBGL_SUPPORTED = true;
}

function checkNull<T>(v: T | null | undefined): T {
    if (!v) throw Error('null error');
    return v;
}

let IS_WEBGL_SUPPORTED: boolean = false;
document.addEventListener('DOMContentLoaded', checkBrowserSupportStatus);
