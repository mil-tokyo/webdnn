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
      opType: "Abs",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("abs", "float v = abs(s);"),
    },
    {
      opType: "Acos",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("acos", "float v = acos(s);"),
    },
    {
      opType: "Acosh",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary(
          "acosh",
          "float v = acosh(s);",
          "float v = log(s + sqrt(s * s - 1.0));"
        ),
    },
    {
      opType: "Asin",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("asin", "float v = asin(s);"),
    },
    {
      opType: "Asinh",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary(
          "asinh",
          "float v = asinh(s);",
          "float v = log(s + sqrt(s * s + 1.0));"
        ),
    },
    {
      opType: "Atan",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("atan", "float v = atan(s);"),
    },
    {
      opType: "Atanh",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary(
          "atanh",
          "float v = atanh(s);",
          "float v = log((s + 1.0) / (1.0 - s)) * 0.5;"
        ),
    },
    {
      opType: "Ceil",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("ceil", "float v = ceil(s);"),
    },
    {
      opType: "Cos",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("cos", "float v = cos(s);"),
    },
    {
      opType: "Cosh",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary(
          "cosh",
          "float v = cosh(s);",
          "float v = (exp(s) + exp(-s)) * 0.5;"
        ),
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
      opType: "HardSwish",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary(
          "hardswish",
          "float v; if (s <= -3.0) { v = 0.0; } else if (s >= 3.0) { v = s; } else { v = s * (s + 3.0) / 6.0; }"
        ),
    },
    {
      opType: "Log",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("log", "float v = log(s);"),
    },
    {
      opType: "Neg",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("neg", "float v = -s;"),
    },
    {
      opType: "Reciprocal",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("neg", "float v = 1.0 / s;"),
    },
    {
      opType: "Relu",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("relu", "float v = max(s, 0.0);"),
    },
    {
      opType: "Round",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary(
          "round",
          "float v = round(s);",
          "float v = floor(s + 0.5);"
        ),
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
      opType: "Sign",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("sign", "float v = sign(s);"),
    },
    {
      opType: "Sin",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("sin", "float v = sin(s);"),
    },
    {
      opType: "Softplus",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("softplus", "float v = log(exp(s) + 1.0);"),
    },
    {
      opType: "Softsign",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new WebGLUnary("softsign", "float v = s / (1.0 + abs(s));"),
    },
    {
      opType: "Sqrt",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("sqrt", "float v = sqrt(s);"),
    },
    {
      opType: "Tan",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("tan", "float v = tan(s);"),
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
