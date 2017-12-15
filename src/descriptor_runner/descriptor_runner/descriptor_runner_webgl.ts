/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import BufferWebGL from "../buffer/buffer_webgl";
import get_weight_decoder from "../decoder/get_weight_decoder";
import webdnnFetch, { readArrayBufferProgressively } from "../fetch";
import { GraphDescriptorWebGL } from "../graph_descriptor/graph_descriptor_webgl";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import * as localforage_ from "../third/localforage.nopromises.min";
import { BackendName, getConfiguration } from "../webdnn";
import WebGLHandler from "../webgl_handler";
import { DescriptorRunner } from "./descriptor_runner";

/**
 * @private
 */
const localforage = localforage_.default;

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
        buffer: BufferWebGL,
        uniformIndex: number
    }[],
    uniforms: {
        func: (...args: any[]) => void,
        args: any[]
    }[],
    xyAttribLoc: number,
    output: BufferWebGL,
    disposable: BufferWebGL[]
}

/**
 * @protected
 */
interface RuntimeInfo {
    inputs: BufferWebGL[],
    outputs: BufferWebGL[]
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
 * @protected
 */
export default class DescriptorRunnerWebGL extends DescriptorRunner<GraphDescriptorWebGL, ArrayBuffer> {
    readonly backendName: BackendName = 'webgl';

    private runtimeInfo: RuntimeInfo;
    private handler: WebGLHandler;
    private vertexShader: WebGLShader;
    private programs: Map<string, WebGLProgram>;
    private buffers: Map<string, BufferWebGL>;

    private inputViews: SymbolicFloat32Array[] | null;
    private outputViews: SymbolicFloat32Array[] | null;

    static checkAvailability() {
        return WebGLHandler.checkAvailability();
    }

    async init() {
        if (!DescriptorRunnerWebGL.checkAvailability()) throw Error('WebGL backend is not supported in this browser.');

        this.handler = WebGLHandler.getInstance();

        let vertexBuffer = this.handler.createArrayBuffer(vertexArray);
        this.handler.bindArrayBuffer(vertexBuffer);

        this.buffers = new Map();
    }

    async fetchDescriptor(directory: string) {
        let res = await webdnnFetch(`${directory}/graph_${this.backendName}_${this.handler.MAX_TEXTURE_SIZE}.json`);
        return res.json();
    }

    async fetchParameters(directory: string, progressCallback?: (loaded: number, total: number) => any) {
        let res = await webdnnFetch(`${directory}/weight_${this.backendName}_${this.handler.MAX_TEXTURE_SIZE}.bin`);
        return readArrayBufferProgressively(res, progressCallback);
    }

    /**
     * Load cached descriptor from WebStorage
     * @protected
     */
    async restoreCachedDescriptor(directory: string): Promise<GraphDescriptorWebGL | null> {
        return localforage.getItem<GraphDescriptorWebGL>(`${directory}_${this.backendName}_${this.handler.MAX_TEXTURE_SIZE}_descriptor`).catch(() => null);
    }

    /**
     * Load cached descriptor from WebStorage
     * @protected
     */
    async restoreCachedParameters(directory: string, progressCallback?: (loaded: number, total: number) => any): Promise<ArrayBuffer | null> {
        let parameter = await localforage.getItem<ArrayBuffer>(`${directory}_${this.backendName}_${this.handler.MAX_TEXTURE_SIZE}_parameters`).catch(() => null);
        if (parameter && progressCallback) progressCallback(parameter.byteLength, parameter.byteLength);
        return parameter
    }

    /**
     * save cache
     */
    async saveCache(directory: string, descriptor: GraphDescriptorWebGL, parameters: ArrayBuffer): Promise<void> {
        await Promise.all([
            localforage.setItem(`${directory}_${this.backendName}_${this.handler.MAX_TEXTURE_SIZE}_descriptor`, descriptor),
            localforage.setItem(`${directory}_${this.backendName}_${this.handler.MAX_TEXTURE_SIZE}_parameters`, parameters)
        ]);
    };

    async setDescriptorAndParameters(descriptor: GraphDescriptorWebGL, parameters: ArrayBuffer) {
        await this.setDescriptor(descriptor);
        await this.compile();

        await this.initializeStaticBuffer(parameters);
        if (this.placeholderContext && this.placeholderContext.isResolved) await this.initializeDynamicBuffer();
    }

    private async initializeStaticBuffer(weightRawArray: ArrayBuffer) {
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        let descriptor = this.descriptor;

        let decoder = get_weight_decoder(this.descriptor.weight_encoding);
        let weight = await decoder.decode(new Uint8Array(weightRawArray));
        let buffers = this.buffers;
        let mapping = descriptor.memory_layout.mapping;

        Object.entries(descriptor.memory_layout.static.allocations)
            .forEach(([name, {width, height, size, channel_mode}]) => {
                buffers.set(name, new BufferWebGL(size * Float32Array.BYTES_PER_ELEMENT, width, height, name, null, channel_mode));
            });

        Object.entries(descriptor.constants_map)
            .forEach(([name, {size, byte_offset}]) => {
                buffers.get(name)!.array.set(new Float32Array(weight.buffer, byte_offset, size));
            });

        (await this.getInputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(mapping[view.name])!.getWriteView(0, view.length, Float32Array).buffer));

        (await this.getOutputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(mapping[view.name])!.getReadView(0, view.length, Float32Array).buffer));
    }

    private async initializeDynamicBuffer() {
        if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
        if (!this.placeholderContext) throw Error("PlaceholderContext is not initialized.");
        let descriptor = this.descriptor;

        let placeholderContext = this.placeholderContext;
        let buffers = this.buffers;
        let mapping = descriptor.memory_layout.mapping;

        Object.entries(descriptor.memory_layout.dynamic.allocations)
            .forEach(([name, {width, height, size, channel_mode}]) => {
                buffers.set(name, new BufferWebGL(placeholderContext.resolve(size) * Float32Array.BYTES_PER_ELEMENT,
                    placeholderContext.resolve(width), placeholderContext.resolve(height), name, null, channel_mode));
            });

        (await this.getInputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(mapping[view.name])!.getWriteView(0, placeholderContext.resolve(view.length), Float32Array).buffer));

        (await this.getOutputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(mapping[view.name])!.getReadView(0, placeholderContext.resolve(view.length), Float32Array).buffer));

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
        this.vertexShader = this.handler.createVertexShader(`
            precision highp float;
            attribute vec2 _xy;
            void main() { 
              gl_Position = vec4(_xy, 0, 1); 
            }
        `);

        Object.keys(descriptor.shader_sources)
            .forEach(name => {
                let fragmentShader = this.handler.createFragmentShader(descriptor.shader_sources[name]);
                let program = this.handler.createProgram(this.vertexShader, fragmentShader);

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
        if (Object.keys(this.descriptor.placeholders).length > 0) throw Error('Currently, WebGL backend doesn\'t support Placeholder feature.')
    }

    getInputViews() {
        if (this.inputViews) return this.inputViews;

        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');

        let descriptor = this.descriptor;
        let placeholderContext = this.placeholderContext;
        let mapping = this.descriptor.memory_layout.mapping;

        this.inputViews = descriptor.inputs.map(name => {
            let view = new SymbolicFloat32Array({
                name: name,
                size: this.buffers.get(mapping[name])!.length,
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
        let mapping = this.descriptor.memory_layout.mapping;

        this.outputViews = descriptor.outputs.map(name => {
            let view = new SymbolicFloat32Array({
                name: name,
                size: this.buffers.get(mapping[name])!.length,
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

        let gl = this.handler.gl;
        let buffers = this.buffers;
        let mapping = this.descriptor.memory_layout.mapping;
        let referenceCount = new Map<WebGLBuffer, number>();

        this.runtimeInfo = {
            inputs: this.getInputViews().map(view => buffers.get(mapping[view.name])!),
            outputs: this.getOutputViews().map(view => buffers.get(mapping[view.name])!),
            programs: this.descriptor.exec_infos.map(execInfo => {
                // inputs
                let inputs = execInfo.inputs.map(input => {
                    let buffer = buffers.get(mapping[input.variable_name])!;

                    if (!referenceCount.has(buffer)) referenceCount.set(buffer, 0);
                    referenceCount.set(buffer, referenceCount.get(buffer)! + 1);

                    return {
                        buffer: buffer,
                        uniformIndex: input.value
                    }
                });

                //output
                let output = buffers.get(mapping[execInfo.output])!;

                // shader
                let program = this.programs.get(execInfo.shader_name)!;
                this.handler.useProgram(program);

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

                        case 'vec3':
                            return {
                                func: gl.uniform3fv,
                                args: [gl.getUniformLocation(program, name), value]
                            };


                        case 'vec4':
                            return {
                                func: gl.uniform4fv,
                                args: [gl.getUniformLocation(program, name), value]
                            };

                        case 'ivec2':
                            return {
                                func: gl.uniform2iv,
                                args: [gl.getUniformLocation(program, name), value]
                            };

                        case 'ivec3':
                            return {
                                func: gl.uniform3iv,
                                args: [gl.getUniformLocation(program, name), value]
                            };


                        case 'ivec4':
                            return {
                                func: gl.uniform4iv,
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

                // attributes
                let xyAttribLoc = gl.getAttribLocation(program, '_xy');

                // run
                return {
                    program: program,
                    frameBuffer: this.handler.createFrameBuffer(),
                    name: execInfo.shader_name,
                    width: output.textureWidth,
                    height: output.textureHeight,
                    inputs: inputs,
                    output: output,
                    xyAttribLoc: xyAttribLoc,
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
        // if (this._running) throw new Error('Calling another run() while running.');
        if (!this.descriptor) throw new Error('Descriptor is not loaded');
        if (!this.inputViews || !this.outputViews) throw new Error('getInputViews and getOutputViews must be called prior to run');
        if (!this.placeholderContext) throw new Error('PlaceholderContext is not initialized');
        if (!this.placeholderContext.isResolved) throw new Error(`Not all placeholders are resolved: ${this.placeholderContext}`);

        let gl = this.handler.gl;
        let runtimeInfo = this.runtimeInfo;

        if (this.runtimeInfo.programs.length > 0) {
            for (let buffer of runtimeInfo.inputs) await buffer.syncWriteViews();

            if (getConfiguration('DEBUG', false)) {
                let records: any = [];
                let totalElapsedTime = 0;

                for (let runtimeProgramInfo of runtimeInfo.programs) {
                    let start = performance.now();

                    this.handler.bindFrameBuffer(runtimeProgramInfo.frameBuffer, runtimeProgramInfo.width, runtimeProgramInfo.height);

                    // inputs
                    for (let {buffer, uniformIndex} of runtimeProgramInfo.inputs) await buffer.bindToReadTexture(uniformIndex);

                    // output
                    runtimeProgramInfo.output.bindToDrawTexture();

                    // shader
                    this.handler.useProgram(runtimeProgramInfo.program);

                    // uniforms
                    for (let uniform of runtimeProgramInfo.uniforms) uniform.func.apply(gl, uniform.args);

                    // attribute
                    gl.vertexAttribPointer(runtimeProgramInfo.xyAttribLoc, 2, gl.FLOAT, true, 8, 0);
                    gl.enableVertexAttribArray(runtimeProgramInfo.xyAttribLoc);

                    // run
                    gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexArray.length / 2);
                    await this.handler.waitForComplete();
                    let elapsedTime = performance.now() - start;
                    totalElapsedTime += elapsedTime;

                    let xs: Float32Array[] = [];
                    for (let {buffer} of runtimeProgramInfo.inputs) {
                        buffer.unbindFromReadTexture();
                        await buffer.syncReadViews();
                        xs.push(buffer.array.slice());
                    }

                    runtimeProgramInfo.output.unbindFromDrawTexture();
                    await runtimeProgramInfo.output.syncReadViews();
                    let y = runtimeProgramInfo.output.array.slice();

                    records.push({
                        'Kernel': runtimeProgramInfo.name,
                        'Elapsed time [ms]': elapsedTime,
                        'xs': xs,
                        'y': y
                    });
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
                    this.handler.bindFrameBuffer(runtimeProgramInfo.frameBuffer, runtimeProgramInfo.width, runtimeProgramInfo.height);

                    // inputs
                    for (let {buffer, uniformIndex} of runtimeProgramInfo.inputs) await buffer.bindToReadTexture(uniformIndex);

                    // output
                    runtimeProgramInfo.output.bindToDrawTexture();

                    // shader
                    this.handler.useProgram(runtimeProgramInfo.program);

                    // uniforms
                    for (let uniform of runtimeProgramInfo.uniforms) uniform.func.apply(gl, uniform.args);

                    // attribute
                    gl.vertexAttribPointer(runtimeProgramInfo.xyAttribLoc, 2, gl.FLOAT, true, 8, 0);
                    gl.enableVertexAttribArray(runtimeProgramInfo.xyAttribLoc);

                    // run
                    gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexArray.length / 2);

                    // release buffers and binding
                    // for (let buffer of runtimeProgramInfo.disposable) buffer.releaseGPUMemory();
                    for (let {buffer} of runtimeProgramInfo.inputs) buffer.unbindFromReadTexture();
                    runtimeProgramInfo.output.unbindFromDrawTexture();
                }
            }

            for (let buffer of runtimeInfo.outputs) await buffer.syncReadViews();
        }

    }
}
