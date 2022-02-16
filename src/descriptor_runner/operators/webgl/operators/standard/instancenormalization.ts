import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { arrayProd, getAttrInt } from "../../../operatorUtil";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenOutputVec4,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorNDGetVec4,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { WebGLTensor } from "../../../../interface/backend/webgl/webglTensor";
import { OperatorEntry } from "../../../../interface/core/operator";

// Opset 1
export class InstanceNormalization extends OperatorImpl {
  epsilon!: number;

  constructor() {
    super("webgl");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.epsilon = getAttrInt(attribute, "epsilon", 1e-5);
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const [input, scale, bias] = inputs;
    if (!context.webgl2) {
      // mean, stdの2要素を出力することが難しいため
      throw new Error("InstanceNormalization: WebGL1 is not supported");
    }

    const reductionLength = arrayProd(input.dims.slice(2));
    const [dimBatch, dimCh] = input.dims;

    // 統計量計算
    const maxSumExpTensor = context.emptyTensor(
      [dimBatch * dimCh * 4],
      "float32",
      { dimPerPixel: 4 }
    );
    await this.calcStat(
      context,
      dimBatch,
      dimCh,
      reductionLength,
      this.epsilon,
      input,
      scale,
      bias,
      maxSumExpTensor
    );

    // 結果計算
    const output = context.emptyTensor(input.dims, input.dataType);
    await this.calcOutput2(
      context,
      dimBatch,
      dimCh,
      reductionLength,
      input,
      maxSumExpTensor,
      output
    );
    maxSumExpTensor.dispose();
    return [output];
  }

  private async calcStat(
    context: WebDNNWebGLContext,
    batchLength: number,
    chLength: number,
    reductionLength: number,
    epsilon: number,
    input: WebGLTensor,
    scale: WebGLTensor,
    bias: WebGLTensor,
    maxSumExpTensor: WebGLTensor
  ) {
    const kernelName = `instancenormalization_stats_${reductionLength}`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

#define reductionLength ${reductionLength}
uniform float epsilon;
${shaderGenTensorOutputUniform(2)}
${shaderGenTensorNDGet("tex_input", 3, context.webgl2)}
${shaderGenTensorNDGet("tex_scale", 1, context.webgl2)}
${shaderGenTensorNDGet("tex_bias", 1, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(2)}
  float s_sum = 0.0;
  float s_sqsum = 0.0;
  for (int i = 0; i < reductionLength; i++) {
    float v = get_tex_input(tex_output_0, tex_output_1, i);
    s_sum += v;
    s_sqsum += v * v;
  }
  float s_mean = s_sum / float(reductionLength);
  float s_var = s_sqsum / float(reductionLength) - s_mean * s_mean + epsilon;
  float s_invstd = inversesqrt(s_var);
  float s_scale = get_tex_scale(tex_output_1) * s_invstd;
  float s_bias = -s_mean * s_scale + get_tex_bias(tex_output_1);

  vec4 s = vec4(s_scale, s_bias, 0.0, 0.0);
  ${shaderGenOutputVec4("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);
    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [chLength * reductionLength, reductionLength, 1],
        input,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_scale",
        scale.strides,
        scale,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_bias",
        bias.strides,
        bias,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [batchLength, chLength],
        maxSumExpTensor,
        context.webgl2
      ),
      { name: "epsilon", value: epsilon, type: "float" },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: input, name: "tex_input" },
        { tensor: scale, name: "tex_scale" },
        { tensor: bias, name: "tex_bias" },
      ],
      maxSumExpTensor,
      uniforms
    );
  }

  private async calcOutput2(
    context: WebDNNWebGLContext,
    batchLength: number,
    chLength: number,
    reductionLength: number,
    input: WebGLTensor,
    maxSumExpTensor: WebGLTensor,
    output: WebGLTensor
  ) {
    const kernelName = `instancenormalization_output`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

${shaderGenTensorOutputUniform(3)}

${shaderGenTensorNDGet("tex_input", 3, context.webgl2)}
${shaderGenTensorNDGetVec4("tex_stats", 2, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(3)}
  vec4 m = get_vec4_tex_stats(tex_output_0, tex_output_1);
  float v = get_tex_input(tex_output_0, tex_output_1, tex_output_2);
  float s = v * m.r + m.g;
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);
    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [chLength * reductionLength, reductionLength, 1],
        input,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_stats",
        [chLength, 1],
        maxSumExpTensor,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [batchLength, chLength, reductionLength],
        output,
        context.webgl2
      ),
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: input, name: "tex_input" },
        { tensor: maxSumExpTensor, name: "tex_stats" },
      ],
      output,
      uniforms
    );
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "InstanceNormalization",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new InstanceNormalization(),
    },
  ];
}
