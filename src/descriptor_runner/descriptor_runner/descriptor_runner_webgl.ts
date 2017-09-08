/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { BufferWebGL, TextureManager } from "../buffer/buffer_webgl";
import get_weight_decoder from "../decoder/get_weight_decoder";
import webdnnFetch, { readArrayBufferProgressively } from "../fetch";
import { GraphDescriptorWebGL } from "../graph_descriptor/graph_descriptor_webgl";
import PlaceholderContext from "../placeholder";
import SymbolicFloat32Array from "../symbolic_typed_array/symbolic_float32array";
import { BackendName, isDebugMode } from "../webdnn";
import WebGLHandler, { WebGLVertexArray } from "../webgl_handler";
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
        buffer: BufferWebGL,
        uniformIndex: number
    }[],
    uniforms: {
        func: (...args: any[]) => void,
        args: any[]
    }[],
    vao: WebGLVertexArray,
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
export default class DescriptorRunnerWebGL extends DescriptorRunner<GraphDescriptorWebGL> {
    readonly backendName: BackendName = 'webgl';

    private runtimeInfo: RuntimeInfo;
    private handler: WebGLHandler;
    private vertexShader: WebGLShader;
    private programs: Map<string, WebGLProgram>;
    private buffers: Map<string, BufferWebGL>;

    private inputViews: SymbolicFloat32Array[] | null;
    private outputViews: SymbolicFloat32Array[] | null;

    static checkAvailability() {
        //TODO(Kiikurage)
        // Safari supports WebGL with OES_TEXTURE_FLOAT extension. However,
        // currently when WebGLRenderingContext#readPixels is called, an error is thrown.
        const IS_SAFARI = navigator.userAgent.toLowerCase().indexOf('safari') !== -1 &&
            navigator.userAgent.toLowerCase().indexOf('chrome') === -1;
        return WebGLHandler.checkAvailability() && !IS_SAFARI;
    }

    async init() {
        if (!DescriptorRunnerWebGL.checkAvailability()) throw Error('WebGL backend is not supported in this browser.');

        this.handler = new WebGLHandler();

        TextureManager.init(this.handler);

        let vertexBuffer = this.handler.createArrayBuffer(vertexArray);
        this.handler.bindArrayBuffer(vertexBuffer);

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

        Object.entries(descriptor.memory_layout.static.allocations)
            .forEach(([name, {width, height, size, channel_mode}]) => {
                buffers.set(name, new BufferWebGL(this.handler.gl, size * Float32Array.BYTES_PER_ELEMENT, width, height, name, null, channel_mode));
            });

        Object.entries(descriptor.constants_map)
            .forEach(([name, {size, byte_offset}]) => {
                buffers.get(name)!.array.set(new Float32Array(weight.buffer, byte_offset, size));
            });

        (await this.getInputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(view.name)!.getWriteView(0, view.length, Float32Array).buffer));

        (await this.getOutputViews())
            .filter(view => !view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(view.name)!.getReadView(0, view.length, Float32Array).buffer));
    }

    private async initializeDynamicBuffer() {
        if (!this.descriptor) throw Error("GraphDescriptor is not loaded.");
        if (!this.placeholderContext) throw Error("PlaceholderContext is not initialized.");
        let descriptor = this.descriptor;

        let placeholderContext = this.placeholderContext;
        let buffers = this.buffers;

        Object.entries(descriptor.memory_layout.dynamic.allocations)
            .forEach(([name, {width, height, size, channel_mode}]) => {
                buffers.set(name, new BufferWebGL(this.handler.gl, placeholderContext.resolve(size) * Float32Array.BYTES_PER_ELEMENT,
                    placeholderContext.resolve(width), placeholderContext.resolve(height), name, null, channel_mode));
            });

        (await this.getInputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(view.name)!.getWriteView(0, placeholderContext.resolve(view.length), Float32Array).buffer));

        (await this.getOutputViews())
            .filter(view => view.isDynamic)
            .forEach(view => view.setArrayBuffer(buffers.get(view.name)!.getReadView(0, placeholderContext.resolve(view.length), Float32Array).buffer));

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
            let view = new SymbolicFloat32Array({
                name: name,
                size: this.buffers.get(name)!.length,
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
            let view = new SymbolicFloat32Array({
                name: name,
                size: this.buffers.get(name)!.length,
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
        let referenceCount = new Map<WebGLBuffer, number>();

        this.runtimeInfo = {
            inputs: this.getInputViews().map(view => buffers.get(view.name)!),
            outputs: this.getOutputViews().map(view => buffers.get(view.name)!),
            programs: this.descriptor.exec_infos.map(execInfo => {
                // inputs
                let inputs = execInfo.inputs.map(input => {
                    let buffer = buffers.get(input.variable_name)!;

                    if (!referenceCount.has(buffer)) referenceCount.set(buffer, 0);
                    referenceCount.set(buffer, referenceCount.get(buffer)! + 1);

                    return {
                        buffer: buffer,
                        uniformIndex: input.value
                    }
                });

                //output
                let output = buffers.get(execInfo.output)!;

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
                let vao = this.handler.createVertexArray();
                this.handler.bindVertexArray(vao);

                // attributes
                let loc = gl.getAttribLocation(program, '_xy');
                gl.vertexAttribPointer(loc, 2, gl.FLOAT, true, 8, 0);
                gl.enableVertexAttribArray(loc);

                // run
                return {
                    program: program,
                    frameBuffer: this.handler.createFrameBuffer(),
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

        let gl = this.handler.gl;
        let runtimeInfo = this.runtimeInfo;

        if (this.runtimeInfo.programs.length > 0) {
            for (let buffer of runtimeInfo.inputs) await buffer.syncWriteViews();

            if (isDebugMode()) {
                let records: any = [];
                let totalElapsedTime = 0;

                for (let runtimeProgramInfo of runtimeInfo.programs) {
                    let start = performance.now();

                    this.handler.bindVertexArray(runtimeProgramInfo.vao);
                    this.handler.bindFrameBuffer(runtimeProgramInfo.frameBuffer, runtimeProgramInfo.width, runtimeProgramInfo.height);

                    // inputs
                    for (let {buffer, uniformIndex} of runtimeProgramInfo.inputs) await buffer.bindToReadTexture(uniformIndex);

                    // output
                    runtimeProgramInfo.output.bindToDrawTexture();

                    // shader
                    this.handler.useProgram(runtimeProgramInfo.program);

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
                        buffer.unbindFromReadTexture();
                        await buffer.syncReadViews();
                        console.log(uniformIndex, buffer.array);
                    }

                    runtimeProgramInfo.output.unbindFromDrawTexture();
                    await runtimeProgramInfo.output.syncReadViews();
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
                    this.handler.bindVertexArray(runtimeProgramInfo.vao);
                    this.handler.bindFrameBuffer(runtimeProgramInfo.frameBuffer, runtimeProgramInfo.width, runtimeProgramInfo.height);

                    // inputs
                    for (let {buffer, uniformIndex} of runtimeProgramInfo.inputs) await buffer.bindToReadTexture(uniformIndex);

                    // output
                    runtimeProgramInfo.output.bindToDrawTexture();

                    // shader
                    this.handler.useProgram(runtimeProgramInfo.program);

                    // uniforms
                    for (let uniform of runtimeProgramInfo.uniforms) uniform.func.apply(gl, uniform.args);

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

        this._running = false;
    }
}
