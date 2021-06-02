import { DataArrayTypes, DataType } from "../../interface/core/constants";
import {
  shaderGenHeader,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../operators/webgl/shaderHelper";
import { TensorImpl } from "../../core/tensorImpl";
import { WebDNNWebGLContextImpl, WebGLSharedTexture } from "./webglContextImpl";
import { WebGLTensor } from "../../interface/backend/webgl/webglTensor";
import { WebGLUniformItem } from "../../interface/backend/webgl/webglContext";

export class WebGLTensorImpl extends TensorImpl implements WebGLTensor {
  textureWidth: number;

  textureHeight: number;

  sharedTexture: WebGLSharedTexture;

  private isBoundToDrawFrameBuffer = false;

  private readTextureUnitIndices: number[] = [];

  constructor(
    private context: WebDNNWebGLContextImpl,
    dims: ReadonlyArray<number>,
    dataType: DataType = "float32",
    public readonly dimPerPixel: 1 | 4 = 1,
    sharedTexture?: WebGLSharedTexture
  ) {
    super(dims, dataType, "webgl");
    if (dataType !== "float32") {
      throw new Error("WebGLTensor only supports float32");
    }
    const pixels = Math.ceil(this.length / dimPerPixel);
    // This makes computing slightly slow. why?
    // this.textureWidth = Math.pow(
    //   2,
    //   Math.ceil(Math.log2(Math.min(pixels, this.context.maxTextureSize)))
    // );
    this.textureWidth = this.context.maxTextureSize;
    this.textureHeight = Math.ceil(pixels / this.textureWidth);
    if (this.textureHeight > this.context.maxTextureSize) {
      throw new Error(
        `Cannot allocate texture of size ${this.length} in this environment. Please split large tensor in the model.`
      );
    }
    if (sharedTexture) {
      this.sharedTexture = sharedTexture;
    } else {
      this.sharedTexture = new WebGLSharedTexture(
        this.context,
        this.textureWidth,
        this.textureHeight,
        this.dimPerPixel
      );
    }
  }

  getTexture(): WebGLTexture {
    return this.sharedTexture.texture;
  }

  alias(dims: ReadonlyArray<number>): WebGLTensorImpl {
    this.sharedTexture.incrRef();
    return new WebGLTensorImpl(
      this.context,
      dims,
      this.dataType,
      this.dimPerPixel,
      this.sharedTexture
    );
  }

  async getData(): Promise<DataArrayTypes> {
    const { gl } = this.context;
    let data: Float32Array;

    if (
      this.context.isWebGL2(gl) &&
      this.context.canOnlyReadRGBA &&
      this.dimPerPixel === 1
    ) {
      // RGBAにパックしてから読み取る必要がある
      const packed = await this.packToRGBA();
      data = (await packed.getData()) as Float32Array;
      packed.dispose();
      return data;
    }

    this.bindToDrawTexture();
    if (this.context.isWebGL2(gl)) {
      const buf = new Float32Array(
        this.textureHeight * this.textureWidth * this.dimPerPixel
      );
      gl.readPixels(
        0,
        0,
        this.textureWidth,
        this.textureHeight,
        this.dimPerPixel === 1 ? gl.RED : gl.RGBA,
        gl.FLOAT,
        buf
      );
      data = new Float32Array(buf.buffer, 0, this.length);
    } else {
      const buf = new Uint8Array(this.textureHeight * this.textureWidth * 4);
      gl.readPixels(
        0,
        0,
        this.textureWidth,
        this.textureHeight,
        gl.RGBA,
        gl.UNSIGNED_BYTE,
        buf
      );
      data = this.unpackColor(buf);
    }
    this.unbindFromDrawTexture();
    return data;
  }

  private unpackColor(buf: Uint8Array): Float32Array {
    // unpack 8bit texture according to shaderHelper
    const unpacked = new Float32Array(this.length);
    for (let i = 0; i < this.length; i++) {
      const b0 = buf[i * 4];
      const b1 = buf[i * 4 + 1];
      const b2 = buf[i * 4 + 2];
      const b3 = buf[i * 4 + 3];
      let val = 0.0;
      if (b0 > 0) {
        let sign: number, exponent: number;
        if (b0 >= 128) {
          sign = 1.0;
          exponent = b0 - 192;
        } else {
          sign = -1.0;
          exponent = b0 - 64;
        }
        const scaled = b1 / 255 + b2 / (255 * 255) + b3 / (255 * 255 * 255);
        val = scaled * Math.pow(2, exponent) * sign;
      }
      unpacked[i] = val;
    }
    return unpacked;
  }

  async setData(data: DataArrayTypes): Promise<void> {
    const { gl } = this.context;
    this.bindToReadTexture(9);
    if (this.context.isWebGL2(gl)) {
      const buf = new Float32Array(
        this.textureWidth * this.textureHeight * this.dimPerPixel
      );
      buf.set(data);
      gl.texSubImage2D(
        gl.TEXTURE_2D,
        0,
        0,
        0,
        this.textureWidth,
        this.textureHeight,
        this.dimPerPixel === 1 ? gl.RED : gl.RGBA,
        gl.FLOAT,
        buf
      );
    } else {
      const buf = this.packColor(data);
      gl.texSubImage2D(
        gl.TEXTURE_2D,
        0,
        0,
        0,
        this.textureWidth,
        this.textureHeight,
        gl.RGBA,
        gl.UNSIGNED_BYTE,
        buf
      );
    }

    this.unbindFromReadTexture();
  }

  private packColor(data: DataArrayTypes): Uint8Array {
    const packed = new Uint8Array(this.textureWidth * this.textureHeight * 4);
    for (let i = 0; i < this.length; i++) {
      const val = data[i];
      let b0 = 0,
        b1 = 0,
        b2 = 0,
        b3 = 0;
      if (val !== 0.0) {
        const sign = val > 0.0 ? 192 : 64;
        const absval = Math.abs(val);
        const exponent = Math.ceil(Math.log2(absval) + 0.0001);
        const scaled = absval * Math.pow(2, -exponent);
        let s1 = scaled;
        let s2 = scaled * 255;
        s2 -= Math.trunc(s2);
        s1 -= s2 / 255;
        let s3 = scaled * (255 * 255);
        s3 -= Math.trunc(s3);
        s2 -= s3 / 255;
        b0 = sign + exponent;
        b1 = Math.min(Math.max(Math.ceil((s1 - 0.5 / 255) * 255), 0), 255);
        b2 = Math.min(Math.max(Math.ceil((s2 - 0.5 / 255) * 255), 0), 255);
        b3 = Math.min(Math.max(Math.ceil((s3 - 0.5 / 255) * 255), 0), 255);
      }
      packed[i * 4] = b0;
      packed[i * 4 + 1] = b1;
      packed[i * 4 + 2] = b2;
      packed[i * 4 + 3] = b3;
    }
    return packed;
  }

  dispose(): void {
    this.sharedTexture.dispose();
  }

  bindToReadTexture(unit: number): void {
    if (this.isBoundToDrawFrameBuffer)
      throw Error(
        "This buffer is already registered as draw buffer. " +
          "You may forgot to unbind the binding while previous operations."
      );

    const { gl } = this.context;

    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, this.getTexture());

    this.readTextureUnitIndices.push(unit);
  }

  unbindFromReadTexture(): void {
    const { gl } = this.context;

    for (const unit of this.readTextureUnitIndices) {
      gl.activeTexture(gl.TEXTURE0 + unit);
      gl.bindTexture(gl.TEXTURE_2D, null);
    }

    this.readTextureUnitIndices = [];
  }

  bindToDrawTexture(): void {
    if (this.readTextureUnitIndices.length > 0)
      throw Error(
        "This buffer is already registered as read buffer. " +
          "You cannot bind a texture as both read and draw texture buffer at same time."
      );
    if (this.isBoundToDrawFrameBuffer)
      throw Error(
        "This buffer is already registered as draw buffer. " +
          "You may forgot to unbind the binding while previous operations."
      );

    const { gl } = this.context;
    gl.viewport(0, 0, this.textureWidth, this.textureHeight);
    gl.scissor(0, 0, this.textureWidth, this.textureHeight);

    gl.framebufferTexture2D(
      gl.FRAMEBUFFER,
      gl.COLOR_ATTACHMENT0,
      gl.TEXTURE_2D,
      this.getTexture(),
      0
    );

    this.isBoundToDrawFrameBuffer = true;
  }

  unbindFromDrawTexture(): void {
    if (!this.isBoundToDrawFrameBuffer) return;

    const { gl } = this.context;

    gl.framebufferTexture2D(
      gl.FRAMEBUFFER,
      gl.COLOR_ATTACHMENT0,
      gl.TEXTURE_2D,
      null,
      0
    );

    this.isBoundToDrawFrameBuffer = false;
  }

  private async packToRGBA(): Promise<WebGLTensorImpl> {
    const outputTensor = new WebGLTensorImpl(
        this.context,
        this.dims,
        "float32",
        4
      ),
      inputPixels = this.length,
      outputPixels = Math.ceil(outputTensor.length / 4),
      kernelName = "RToRGBA";
    if (!this.context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(this.context.webgl2)}
  
${shaderGenTensorOutputUniform(1)}
${shaderGenTensorNDGet("tex_input", 1, this.context.webgl2)}
uniform int input_pixels;

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(1)}
  vec4 result = vec4(0.0, 0.0, 0.0, 0.0);
  int pos = tex_output_0 * 4;
  if (pos < input_pixels) {
    result.r = get_tex_input(pos);
  }
  pos++;
  if (pos < input_pixels) {
    result.g = get_tex_input(pos);
  }
  pos++;
  if (pos < input_pixels) {
    result.b = get_tex_input(pos);
  }
  pos++;
  if (pos < input_pixels) {
    result.a = get_tex_input(pos);
  }
  fragColor = result;
  return;
}
      `;
      this.context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [1],
        [this.textureHeight, this.textureWidth],
        this.context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [outputPixels],
        [outputTensor.textureHeight, outputTensor.textureWidth],
        this.context.webgl2
      ),
      { name: "input_pixels", type: "int", value: inputPixels },
    ];

    await this.context.runKernel(
      kernelName,
      [{ tensor: this, name: "tex_input" }],
      outputTensor,
      uniforms
    );
    return outputTensor;
  }
}
