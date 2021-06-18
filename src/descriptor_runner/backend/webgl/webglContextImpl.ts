import { WebDNNCPUContext } from "../../interface/backend/cpu/cpuContext";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../interface/backend/webgl/webglContext";
import { WebGLTensor } from "../../interface/backend/webgl/webglTensor";
import { DataType } from "../../interface/core/constants";
import { Tensor } from "../../interface/core/tensor";
import { nonnull } from "../../util";
import { WebGLTensorImpl } from "./webglTensorImpl";

// [x y u v] * [upper-left, lower-left, upper-right, lower-right]
const vertexArray = new Float32Array([-1, +1, -1, -1, +1, +1, +1, -1]),
  vertex_shader_source_1 = `
precision highp float;
attribute vec2 _xy;
void main() { 
  gl_Position = vec4(_xy, 0, 1); 
}
`,
  vertex_shader_source_2 = `#version 300 es
precision highp float;
in vec2 _xy;
void main() { 
  gl_Position = vec4(_xy, 0, 1); 
}
`;

interface WebGLSharedTexturePoolItem {
  textureWidth: number;
  textureHeight: number;
  dimPerPixel: 1 | 4;
  texture: WebGLTexture;
}

export class WebGLSharedTexture {
  refCount: number;

  texture: WebGLTexture;

  constructor(
    private context: WebDNNWebGLContextImpl,
    public textureWidth: number,
    public textureHeight: number,
    public dimPerPixel: 1 | 4
  ) {
    this.refCount = 1;
    const { gl } = this.context;
    let pooled: WebGLTexture | null = null;
    for (let i = 0; i < this.context.texturePool.length; i++) {
      const item = this.context.texturePool[i];
      if (
        item.textureWidth === textureWidth &&
        item.textureHeight === textureHeight &&
        item.dimPerPixel === dimPerPixel
      ) {
        pooled = item.texture;
        this.context.texturePool.splice(i, 1);
        break;
      }
    }
    if (pooled) {
      this.texture = pooled;
    } else {
      this.texture = nonnull(gl.createTexture());

      gl.activeTexture(gl.TEXTURE0 + 9); // TODO: texture unit 9 is always available?
      gl.bindTexture(gl.TEXTURE_2D, this.texture);
      /*
       * WebGL2: dimPerPixel==1: R channelのみ使用, dimPerPixel==4: RGBAチャンネルを利用（一部の最適化されたオペレータ用）
       * WebGL1: RGBA各8bitにfloatをpackして使用（floatテクスチャ未対応環境を想定）
       */
      if (this.context.isWebGL2(gl)) {
        gl.texImage2D(
          gl.TEXTURE_2D,
          0,
          dimPerPixel === 1 ? gl.R32F : gl.RGBA32F,
          this.textureWidth,
          this.textureHeight,
          0,
          dimPerPixel === 1 ? gl.RED : gl.RGBA,
          gl.FLOAT,
          null
        );
      } else {
        if (dimPerPixel !== 1) {
          throw new Error("colorPerPixel must be 1 in WebGL1");
        }
        gl.texImage2D(
          gl.TEXTURE_2D,
          0,
          gl.RGBA,
          this.textureWidth,
          this.textureHeight,
          0,
          gl.RGBA,
          gl.UNSIGNED_BYTE,
          null
        );
      }

      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
      gl.bindTexture(gl.TEXTURE_2D, null);
    }
  }

  incrRef(): void {
    this.refCount++;
  }

  dispose(): void {
    this.refCount--;
    if (this.refCount <= 0) {
      /*
       * TODO: pool量が多すぎる場合に開放
       * let gl = WebDNNWebGLContext.getInstance().gl;
       * gl.deleteTexture(this.texture);
       */
      this.context.texturePool.push({
        textureWidth: this.textureWidth,
        textureHeight: this.textureHeight,
        dimPerPixel: this.dimPerPixel,
        texture: this.texture,
      });
    }
  }
}

export class WebDNNWebGLContextImpl implements WebDNNWebGLContext {
  backend = "webgl" as const;

  isMac: boolean;

  canOnlyReadRGBA: boolean;

  gl: WebGLRenderingContext | WebGL2RenderingContext;

  vshader!: WebGLShader;

  fb: WebGLFramebuffer;

  webgl2: boolean;

  programs: Map<string, { program: WebGLProgram }> = new Map();

  initialized = false;

  maxTextureSize: number;

  texturePool: WebGLSharedTexturePoolItem[] = [];

  constructor(public cpuContext: WebDNNCPUContext) {
    this.isMac = navigator.userAgent.includes("Mac");
    this.canOnlyReadRGBA = this.isMac;
    const canvas = document.createElement("canvas");
    let gl: WebGLRenderingContext | WebGL2RenderingContext | null = null;
    if (window.location.search.indexOf("webgl1") < 0) {
      gl = canvas.getContext("webgl2");
    } else {
      console.log("option to force using WebGL1");
    }
    if (!gl) {
      gl = canvas.getContext("webgl");
      if (!gl) {
        throw new Error("WebGLRenderingContext initialization failed.");
      }
      this.webgl2 = false;
    } else {
      this.webgl2 = true;
    }
    this.gl = gl;
    if (this.webgl2) {
      // Enable color mode of gl.R32F
      gl.getExtension("EXT_color_buffer_float");
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

    const vertexBuffer = this.createArrayBuffer(vertexArray);
    this.bindArrayBuffer(vertexBuffer);
    this.fb = nonnull(gl.createFramebuffer());
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fb);
    this.maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE) as number;
    if (window.location.search.indexOf("max_texture_size_4096") >= 0) {
      console.warn("Forcing WebGL MAX_TEXTURE_SIZE to 4096");
      this.maxTextureSize = 4096;
    }
  }

  async initialize(): Promise<void> {
    this.initialized = true;
  }

  private checkInitialized() {
    if (!this.initialized) {
      throw new Error("Not initialized");
    }
  }

  isWebGLTensor(tensor: Tensor): tensor is WebGLTensor {
    return tensor.backend === this.backend;
  }

  assertsWebGLTensor(tensor: Tensor): asserts tensor is WebGLTensor {
    if (tensor.backend !== this.backend) {
      throw new Error(
        `Tensor backend ${this.backend} is expected, but ${tensor.backend} is given.`
      );
    }
  }

  assertsWebGLTensorArray(tensors: Tensor[]): asserts tensors is WebGLTensor[] {
    for (const tensor of tensors) {
      if (tensor.backend !== this.backend) {
        throw new Error(
          `Tensor backend ${this.backend} is expected, but ${tensor.backend} is given.`
        );
      }
    }
  }

  emptyTensor(
    dims: ReadonlyArray<number>,
    dataType?: DataType,
    option?: { dimPerPixel?: 1 | 4; textureShape?: ReadonlyArray<number> }
  ): WebGLTensor {
    return new WebGLTensorImpl(
      this,
      dims,
      dataType,
      option?.dimPerPixel,
      option?.textureShape
    );
  }

  async moveTensor(
    tensor: Tensor,
    option: { dimPerPixel?: 1 | 4; textureShape?: ReadonlyArray<number> }
  ): Promise<WebGLTensor> {
    const dst = new WebGLTensorImpl(
      this,
      tensor.dims,
      tensor.dataType,
      option.dimPerPixel,
      option.textureShape
    );
    await dst.setData(await tensor.getData());
    return dst;
  }

  createArrayBuffer(vertexArray: Float32Array): WebGLBuffer {
    const buffer = nonnull(this.gl.createBuffer());
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, buffer);
    this.gl.bufferData(this.gl.ARRAY_BUFFER, vertexArray, this.gl.STATIC_DRAW);

    return buffer;
  }

  bindArrayBuffer(buffer: WebGLBuffer): void {
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, buffer);
  }

  createShader(type: number, source: string): WebGLShader {
    const shader = nonnull(this.gl.createShader(type));

    this.gl.shaderSource(shader, source);
    this.gl.compileShader(shader);
    if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
      console.error(this.gl.getShaderInfoLog(shader));
      throw Error(`Shader Compile failed: ${this.gl.getShaderInfoLog(shader)}`);
    }

    return shader;
  }

  addKernel(name: string, sourceCode: string): void {
    if (this.programs.has(name)) {
      return;
    }
    this.programs.set(name, { program: this.compileKernel(sourceCode) });
  }

  hasKernel(name: string): boolean {
    return this.programs.has(name);
  }

  compileKernel(sourceCode: string): WebGLProgram {
    const { gl } = this;
    if (!this.vshader) {
      this.vshader = this.createShader(
        gl.VERTEX_SHADER,
        this.webgl2 ? vertex_shader_source_2 : vertex_shader_source_1
      );
    }
    const fshader = this.createShader(gl.FRAGMENT_SHADER, sourceCode),
      program = nonnull(this.gl.createProgram());

    this.gl.attachShader(program, fshader);
    this.gl.attachShader(program, this.vshader);
    this.gl.linkProgram(program);
    if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
      console.error(this.gl.getProgramInfoLog(program));
      throw new Error("ShaderProgram Initialization failed.");
    }

    return program;
  }

  async runKernel(
    name: string,
    inputs: { tensor: WebGLTensorImpl; name: string }[],
    output: WebGLTensorImpl,
    uniforms: WebGLUniformItem[]
  ): Promise<void> {
    this.checkInitialized();
    const kobj = this.programs.get(name);
    if (!kobj) {
      throw new Error(`Unknown kernel ${name}`);
    }
    const { gl } = this,
      xyAttribLoc = gl.getAttribLocation(kobj.program, "_xy");
    for (let i = 0; i < inputs.length; i++) {
      inputs[i].tensor.bindToReadTexture(i);
    }
    output.bindToDrawTexture();

    gl.useProgram(kobj.program);

    for (let i = 0; i < inputs.length; i++) {
      gl.uniform1i(gl.getUniformLocation(kobj.program, inputs[i].name), i);
    }

    for (const uniform of uniforms) {
      switch (uniform.type) {
        case "float":
          gl.uniform1f(
            gl.getUniformLocation(kobj.program, uniform.name),
            uniform.value
          );
          break;
        case "int":
          gl.uniform1i(
            gl.getUniformLocation(kobj.program, uniform.name),
            uniform.value
          );
          break;
        default:
          throw new Error();
      }
    }
    gl.vertexAttribPointer(xyAttribLoc, 2, gl.FLOAT, true, 8, 0);
    gl.enableVertexAttribArray(xyAttribLoc);

    gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexArray.length / 2);
    // TODO: 完了を待つかどうか

    for (let i = 0; i < inputs.length; i++) {
      inputs[i].tensor.unbindFromReadTexture();
    }

    output.unbindFromDrawTexture();
  }

  isWebGL2(
    gl: WebGLRenderingContext | WebGL2RenderingContext
  ): gl is WebGL2RenderingContext {
    return this.webgl2;
  }
}
