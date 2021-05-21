import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrInt } from "../../../operatorUtil";
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
export class Softmax extends OperatorImpl {
  axis!: number;

  constructor() {
    super("webgl");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    // TODO: cpuと共通
    super.initialize(attribute);
    this.axis = getAttrInt(attribute, "axis", -1);
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0];
    let { axis } = this;
    if (axis < 0) {
      axis += input.ndim;
    }
    if (axis !== input.ndim - 1) {
      throw new Error(
        "Softmax: currently only reducing final axis is supported"
      );
    }
    // 最終軸のreductionに特化した実装
    const reductionLength = input.dims[axis],
      outerLength = input.length / reductionLength;
    if (context.webgl2) {
      // 最大値計算
      const maxSumExpTensor = context.emptyTensor(
        [outerLength * 4],
        "float32",
        4
      );
      await this.calcMax2(
        context,
        outerLength,
        reductionLength,
        input,
        maxSumExpTensor
      );

      // 結果計算
      const output = context.emptyTensor(input.dims, input.dataType);
      await this.calcOutput2(
        context,
        outerLength,
        reductionLength,
        input,
        maxSumExpTensor,
        output
      );
      maxSumExpTensor.dispose();
      return [output];
    } else {
      // 最大値計算
      const maxTensor = context.emptyTensor([outerLength]);
      await this.calcMax(
        context,
        outerLength,
        reductionLength,
        input,
        maxTensor
      );

      // Sum(exp)計算
      const sumExpTensor = context.emptyTensor([outerLength]);
      await this.calcSumExp(
        context,
        outerLength,
        reductionLength,
        input,
        maxTensor,
        sumExpTensor
      );
      // 結果計算
      const output = context.emptyTensor(input.dims, input.dataType);
      await this.calcOutput(
        context,
        outerLength,
        reductionLength,
        input,
        maxTensor,
        sumExpTensor,
        output
      );
      maxTensor.dispose();
      sumExpTensor.dispose();
      return [output];
    }
  }

  private async calcMax2(
    context: WebDNNWebGLContext,
    outerLength: number,
    reductionLength: number,
    input: WebGLTensor,
    maxSumExpTensor: WebGLTensor
  ) {
    const kernelName = `softmax_max_${reductionLength}`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

#define reductionLength ${reductionLength}
${shaderGenTensorOutputUniform(1)}
uniform sampler2D tex_input;
uniform int tex_input_stride_0;
uniform int tex_input_stride_1;

ivec2 get_coord(int d0) {
  int flat_index = d0 * tex_input_stride_0;
  int texture_w = textureSize(tex_input, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(1)}
  int texture_w = textureSize(tex_input, 0).x;
  ivec2 c_init = get_coord(tex_output_0);
  ivec2 c_i = c_init;
  float s_max = texelFetch(tex_input, c_i, 0).r;
  c_i.x += 1;
  if (c_i.x >= texture_w) {
    c_i = ivec2(0, c_i.y + 1);
  }
  for (int i = 1; i < reductionLength; i++) {
    float v = texelFetch(tex_input, c_i, 0).r;
    if (v > s_max) {
      s_max = v;
    }
    c_i.x += 1;
    if (c_i.x >= texture_w) {
      c_i = ivec2(0, c_i.y + 1);
    }
  }
  c_i = c_init;
  float s_sum_exp = 0.0;
  for (int i = 0; i < reductionLength; i++) {
    float v = texelFetch(tex_input, c_i, 0).r;
    s_sum_exp += exp(v - s_max);
    c_i.x += 1;
    if (c_i.x >= texture_w) {
      c_i = ivec2(0, c_i.y + 1);
    }
  }
  s_sum_exp = 1.0 / s_sum_exp;

  vec4 s = vec4(s_max, s_sum_exp, 0.0, 0.0);
  ${shaderGenOutputVec4("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);
    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [reductionLength, 1],
        input,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [outerLength],
        maxSumExpTensor,
        context.webgl2
      ),
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: input, name: "tex_input" }],
      maxSumExpTensor,
      uniforms
    );
  }

  private async calcOutput2(
    context: WebDNNWebGLContext,
    outerLength: number,
    reductionLength: number,
    input: WebGLTensor,
    maxSumExpTensor: WebGLTensor,
    output: WebGLTensor
  ) {
    const kernelName = `softmax_output`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

${shaderGenTensorOutputUniform(2)}

${shaderGenTensorNDGet("tex_input", 2, context.webgl2)}
${shaderGenTensorNDGetVec4("tex_max_sum_exp", 1, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(2)}
  vec4 m = get_vec4_tex_max_sum_exp(tex_output_0);
  float v = get_tex_input(tex_output_0, tex_output_1);
  float s = exp(v - m.r) * m.g;
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);
    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [reductionLength, 1],
        input,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_max_sum_exp",
        [1],
        maxSumExpTensor,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [outerLength, reductionLength],
        output,
        context.webgl2
      ),
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: input, name: "tex_input" },
        { tensor: maxSumExpTensor, name: "tex_max_sum_exp" },
      ],
      output,
      uniforms
    );
  }

  private async calcMax(
    context: WebDNNWebGLContext,
    outerLength: number,
    reductionLength: number,
    input: WebGLTensor,
    maxTensor: WebGLTensor
  ) {
    const kernelName = `softmax_max_${reductionLength}`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

#define reductionLength ${reductionLength}
${shaderGenTensorOutputUniform(1)}

${shaderGenTensorNDGet("tex_input", 2, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(1)}
  float s = get_tex_input(tex_output_0, 0);
  for (int i = 1; i < reductionLength; i++) {
    float v = get_tex_input(tex_output_0, i);
    if (v > s) {
      s = v;
    }
  }
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);
    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [reductionLength, 1],
        input,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [outerLength],
        maxTensor,
        context.webgl2
      ),
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: input, name: "tex_input" }],
      maxTensor,
      uniforms
    );
  }

  private async calcSumExp(
    context: WebDNNWebGLContext,
    outerLength: number,
    reductionLength: number,
    input: WebGLTensor,
    maxTensor: WebGLTensor,
    sumExpTensor: WebGLTensor
  ) {
    const kernelName = `softmax_sumexp_${reductionLength}`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

#define reductionLength ${reductionLength}
${shaderGenTensorOutputUniform(1)}

${shaderGenTensorNDGet("tex_input", 2, context.webgl2)}
${shaderGenTensorNDGet("tex_max", 1, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(1)}
  float s = 0.0;
  float m = get_tex_max(tex_output_0);
  for (int i = 0; i < reductionLength; i++) {
    float v = get_tex_input(tex_output_0, i);
    s += exp(v - m);
  }
  s = 1.0 / s;
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);
    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [reductionLength, 1],
        input,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_max",
        [1],
        maxTensor,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [outerLength],
        sumExpTensor,
        context.webgl2
      ),
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: input, name: "tex_input" },
        { tensor: maxTensor, name: "tex_max" },
      ],
      sumExpTensor,
      uniforms
    );
  }

  private async calcOutput(
    context: WebDNNWebGLContext,
    outerLength: number,
    reductionLength: number,
    input: WebGLTensor,
    maxTensor: WebGLTensor,
    sumExpTensor: WebGLTensor,
    output: WebGLTensor
  ) {
    const kernelName = `softmax_output`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

${shaderGenTensorOutputUniform(2)}

${shaderGenTensorNDGet("tex_input", 2, context.webgl2)}
${shaderGenTensorNDGet("tex_max", 1, context.webgl2)}
${shaderGenTensorNDGet("tex_sumexp", 1, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(2)}
  float m = get_tex_max(tex_output_0);
  float se = get_tex_sumexp(tex_output_0);
  float v = get_tex_input(tex_output_0, tex_output_1);
  float s = exp(v - m) * se;
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);
    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [reductionLength, 1],
        input,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_max",
        [1],
        maxTensor,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_sumexp",
        [1],
        sumExpTensor,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [outerLength, reductionLength],
        output,
        context.webgl2
      ),
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: input, name: "tex_input" },
        { tensor: maxTensor, name: "tex_max" },
        { tensor: sumExpTensor, name: "tex_sumexp" },
      ],
      output,
      uniforms
    );
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Softmax",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new Softmax(),
    },
  ];
}
