import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { WebGLTensor } from "../../../../interface/backend/webgl/webglTensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Gemm } from "../../../base/gemm";
import { broadcastUni } from "../../../operatorUtil";
import {
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
  shaderGenHeader,
} from "../../shaderHelper";

export class WebGLGemm extends Gemm {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const inputA = inputs[0];
    const inputB = inputs[1];
    const inputC = inputs[2];
    if (inputC) {
      return this.runWithC(context, inputA, inputB, inputC);
    } else {
      throw new Error();
    }
  }
  private async runWithC(
    context: WebDNNWebGLContext,
    inputA: WebGLTensor,
    inputB: WebGLTensor,
    inputC: WebGLTensor
  ): Promise<WebGLTensor[]> {
    const {
      m,
      n,
      k,
      strideA: [strideA0, strideA1],
      strideB: [strideB0, strideB1],
    } = this.calcShape(inputA.dims, inputB.dims);
    const [strideC0, strideC1] = broadcastUni([m, n], inputC.dims);

    if (
      inputA.dimPerPixel !== 1 ||
      inputB.dimPerPixel !== 1 ||
      inputC.dimPerPixel !== 1
    ) {
      throw new Error();
    }

    const outputTensor = context.emptyTensor([m, n], "float32", 1);
    // ループ回数は定数が必要
    const kernelSource = `${shaderGenHeader(context.webgl2)}

#define m ${m}
#define n ${n}
#define k ${k}
${shaderGenTensorOutputUniform(2)}
uniform float alpha;
uniform float beta;

${shaderGenTensorNDGet("tex_input_a", 2, context.webgl2)}
${shaderGenTensorNDGet("tex_input_b", 2, context.webgl2)}
${shaderGenTensorNDGet("tex_input_c", 2, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(2)}
  float s = 0.0;
  for (int ip = 0; ip < k; ip++) {
    s += get_tex_input_a(tex_output_0, ip) * get_tex_input_b(ip, tex_output_1);
  }
  s *= alpha;
  s += beta * get_tex_input_c(tex_output_0, tex_output_1);
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    const kernelName = `gemm_${m}_${n}_${k}`;
    context.addKernel(kernelName, kernelSource);

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_a",
        [strideA0, strideA1],
        inputA,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_b",
        [strideB0, strideB1],
        inputB,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_c",
        [strideC0, strideC1],
        inputC,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([m, n], outputTensor, context.webgl2),
      { name: "alpha", type: "float", value: this.alpha },
      { name: "beta", type: "float", value: this.beta },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: inputA, name: "tex_input_a" },
        { tensor: inputB, name: "tex_input_b" },
        { tensor: inputC, name: "tex_input_c" },
      ],
      outputTensor,
      uniforms
    );
    return [outputTensor];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Gemm",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLGemm(),
    },
  ];
}
