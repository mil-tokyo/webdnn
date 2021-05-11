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

export class WebGLUnary extends OperatorImpl {
  constructor(
    public kernelName: string,
    private unaryCalculationSource: string,
    private unaryCalculationSourceWebGL1?: string
  ) {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0];
    if (input.dataType !== "float32") {
      throw new Error();
    }
    const outputTensor = context.emptyTensor(input.dims, "float32");
    // elementwiseのアクセスにおいてテクスチャサイズが同じであることを仮定
    if (
      input.textureWidth !== outputTensor.textureWidth ||
      input.textureHeight !== outputTensor.textureHeight ||
      input.dimPerPixel !== 1
    ) {
      throw new Error();
    }

    // gl_FragCoord.x: 0.5, 1.5, 2.5, ..., textureWidth-0.5
    // texture2D(textureName, vec2(x, y)): x=(0.5, 1.5, 2.5, ...) / textureWidth
    if (!context.hasKernel(this.kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  ${shaderGenTensorElementwiseGet("tex_input", context.webgl2)}
  void main() {
    float s = get_tex_input();
    ${
      !context.webgl2 && this.unaryCalculationSourceWebGL1
        ? this.unaryCalculationSourceWebGL1
        : this.unaryCalculationSource
    }
    ${shaderGenOutput("v", context.webgl2)}
    return;
  }
      `;
      context.addKernel(this.kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorElementwiseGetUniformItem(
        "tex_input",
        input,
        context.webgl2
      ),
    ];

    await context.runKernel(
      this.kernelName,
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
      opType: "Ceil",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("ceil", "float v = ceil(s);"),
    },
    {
      opType: "Exp",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("exp", "float v = exp(s);"),
    },
    {
      opType: "Floor",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("floor", "float v = floor(s);"),
    },
    {
      opType: "Relu",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("relu", "float v = max(s, 0.0);"),
    },
    {
      opType: "Sigmoid",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary(
          "sigmoid",
          "float v = (tanh(s * 0.5) + 1.0) * 0.5;",
          "float v = 1.0 / (1.0 + exp(-s));"
        ),
    },
    {
      opType: "Sqrt",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("sqrt", "float v = sqrt(s);"),
    },
    {
      opType: "Tanh",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary(
          "tanh",
          "float v = tanh(s);",
          "float vt = exp(-2.0 * s); float v = (1.0 - vt) / (1.0 + vt);"
        ),
    },
  ];
}
