import { OperatorImpl } from "../../../operatorImpl";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorElementwiseGet,
  shaderGenTensorElementwiseGetUniformItem,
} from "../../shaderHelper";
import { OperatorEntry } from "../../../../interface/core/operator";
import { onnx } from "onnx-proto";
import { getAttrFloat } from "../../../operatorUtil";

export class WebGLClip extends OperatorImpl {
  clipMax!: number;
  clipMin!: number;

  constructor() {
    super("webgl");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.clipMax = getAttrFloat(attribute, "max", 65536);
    this.clipMin = getAttrFloat(attribute, "min", -65536);
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0];
    if (input.dataType !== "float32") {
      throw new Error();
    }
    const outputTensor = context.emptyTensor(input.dims, "float32");
    // Elementwiseのアクセスにおいてテクスチャサイズが同じであることを仮定
    if (
      input.textureWidth !== outputTensor.textureWidth ||
      input.textureHeight !== outputTensor.textureHeight ||
      input.dimPerPixel !== 1
    ) {
      throw new Error();
    }

    /*
     * Gl_FragCoord.x: 0.5, 1.5, 2.5, ..., textureWidth-0.5
     * texture2D(textureName, vec2(x, y)): x=(0.5, 1.5, 2.5, ...) / textureWidth
     */
    const kernelName = `clip_${this.clipMax}_${this.clipMin}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  ${shaderGenTensorElementwiseGet("tex_input", context.webgl2)}
  void main() {
    float s = get_tex_input();
    float v = clamp(s, ${this.clipMin.toExponential()}, ${this.clipMax.toExponential()});
    ${shaderGenOutput("v", context.webgl2)}
    return;
  }
      `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorElementwiseGetUniformItem(
        "tex_input",
        input,
        context.webgl2
      ),
    ];

    await context.runKernel(
      kernelName,
      [{ tensor: input, name: "tex_input" }],
      outputTensor,
      uniforms
    );
    return [outputTensor];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Clip",
      backend: "webgl",
      opsetMin: 1,
      opsetMax: 11,
      factory: () => new WebGLClip(),
    },
  ];
}
