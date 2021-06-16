import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";
import { MatMul } from "../../../base/matmul";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { WebGLTensor } from "../../../../interface/backend/webgl/webglTensor";
import { OperatorEntry } from "../../../../interface/core/operator";

// Version 13
export class WebGLMatMul extends MatMul {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const inputA = inputs[0],
      inputB = inputs[1];
    if (inputA.dataType !== "float32" || inputB.dataType !== "float32") {
      throw new Error("only float32 is supported");
    }
    if (inputA.dimPerPixel !== 1 || inputB.dimPerPixel !== 1) {
      throw new Error();
    }
    const {
        resultLength,
        resultDims,
        resultStrides,
        resultDimsAfterSqueeze,
        stridesA,
        stridesB,
        innerProductLength,
      } = this.calcShape(inputA.dims, inputB.dims),
      output = context.emptyTensor(resultDimsAfterSqueeze, "float32");
    if (resultDims.length === 2) {
      await this.calcDim2(
        context,
        inputA,
        inputB,
        output,
        resultDims,
        resultStrides,
        stridesA,
        stridesB,
        innerProductLength
      );
    } else if (resultDims.length === 3) {
      await this.calcDim3(
        context,
        inputA,
        inputB,
        output,
        resultDims,
        resultStrides,
        stridesA,
        stridesB,
        innerProductLength
      );
    } else {
      // TODO: 4次元以上のサポート
      throw new Error();
    }

    return [output];
  }

  private async calcDim2(
    context: WebDNNWebGLContext,
    dA: WebGLTensor,
    dB: WebGLTensor,
    dC: WebGLTensor,
    resultDims: number[],
    resultStrides: number[],
    stridesA: ReadonlyArray<number>,
    stridesB: ReadonlyArray<number>,
    innerProductLength: number
  ) {
    const kernelSource = context.webgl2
        ? `${shaderGenHeader(context.webgl2)}

#define innerProductLength ${innerProductLength}
${shaderGenTensorOutputUniform(resultDims.length)}

uniform sampler2D tex_input_a;
uniform int tex_input_a_stride_0;
uniform int tex_input_a_stride_1;

ivec2 get_coord_a(int d0) {
  int flat_index = d0 * tex_input_a_stride_0;
  int texture_w = textureSize(tex_input_a, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

uniform sampler2D tex_input_b;
uniform int tex_input_b_stride_0;
uniform int tex_input_b_stride_1;

ivec2 get_coord_b(int d1, int d2) {
  int flat_index = d1 * tex_input_b_stride_1;
  int texture_w = textureSize(tex_input_b, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(resultDims.length)}
  float s = 0.0;
  ivec2 c_a = get_coord_a(tex_output_0);
  ivec2 c_b = get_coord_b(tex_output_1);
  int texture_w_a = textureSize(tex_input_a, 0).x;
  int texture_w_b = textureSize(tex_input_b, 0).x;
  for (int ip = 0; ip < innerProductLength; ip++) {
    s += texelFetch(tex_input_a, c_a, 0).r * texelFetch(tex_input_b, c_b, 0).r;
    c_a.x += tex_input_a_stride_1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    c_b.x += tex_input_b_stride_0;
    if (c_b.x >= texture_w_b) {
      c_b = ivec2(c_b.x - texture_w_b, c_b.y + 1);
    }
  }
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`
        : `${shaderGenHeader(context.webgl2)}

#define innerProductLength ${innerProductLength}
${shaderGenTensorOutputUniform(resultDims.length)}

${shaderGenTensorNDGet("tex_input_a", 2, context.webgl2)}
${shaderGenTensorNDGet("tex_input_b", 2, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(resultDims.length)}
  float s = 0.0;
  for (int ip = 0; ip < innerProductLength; ip++) {
    s += get_tex_input_a(tex_output_0, ip) * get_tex_input_b(ip, tex_output_1);
  }
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`,
      kernelName = `matmul_2_${innerProductLength}`;
    context.addKernel(kernelName, kernelSource);

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_a",
        stridesA,
        dA,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_b",
        stridesB,
        dB,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(resultDims, dC, context.webgl2),
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dA, name: "tex_input_a" },
        { tensor: dB, name: "tex_input_b" },
      ],
      dC,
      uniforms
    );
  }

  private async calcDim3(
    context: WebDNNWebGLContext,
    dA: WebGLTensor,
    dB: WebGLTensor,
    dC: WebGLTensor,
    resultDims: number[],
    resultStrides: number[],
    stridesA: ReadonlyArray<number>,
    stridesB: ReadonlyArray<number>,
    innerProductLength: number
  ) {
    const kernelSource = context.webgl2
        ? `${shaderGenHeader(context.webgl2)}

#define innerProductLength ${innerProductLength}
${shaderGenTensorOutputUniform(resultDims.length)}

uniform sampler2D tex_input_a;
uniform int tex_input_a_stride_0;
uniform int tex_input_a_stride_1;
uniform int tex_input_a_stride_2;

ivec2 get_coord_a(int d0, int d1) {
  int flat_index = d0 * tex_input_a_stride_0 + d1 * tex_input_a_stride_1;
  int texture_w = textureSize(tex_input_a, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

uniform sampler2D tex_input_b;
uniform int tex_input_b_stride_0;
uniform int tex_input_b_stride_1;
uniform int tex_input_b_stride_2;

ivec2 get_coord_b(int d0, int d2) {
  int flat_index = d0 * tex_input_b_stride_0 + d2 * tex_input_b_stride_2;
  int texture_w = textureSize(tex_input_b, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(resultDims.length)}
  float s = 0.0;
  ivec2 c_a = get_coord_a(tex_output_0, tex_output_1);
  ivec2 c_b = get_coord_b(tex_output_0, tex_output_2);
  int texture_w_a = textureSize(tex_input_a, 0).x;
  int texture_w_b = textureSize(tex_input_b, 0).x;
  for (int ip = 0; ip < innerProductLength; ip++) {
    s += texelFetch(tex_input_a, c_a, 0).r * texelFetch(tex_input_b, c_b, 0).r;
    c_a.x += tex_input_a_stride_2;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    c_b.x += tex_input_b_stride_1;
    if (c_b.x >= texture_w_b) {
      c_b = ivec2(c_b.x - texture_w_b, c_b.y + 1);
    }
  }
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`
        : `${shaderGenHeader(context.webgl2)}

#define innerProductLength ${innerProductLength}
${shaderGenTensorOutputUniform(resultDims.length)}

${shaderGenTensorNDGet("tex_input_a", 3, context.webgl2)}
${shaderGenTensorNDGet("tex_input_b", 3, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(resultDims.length)}
  float s = 0.0;
  for (int ip = 0; ip < innerProductLength; ip++) {
    s += get_tex_input_a(tex_output_0, tex_output_1, ip) * get_tex_input_b(tex_output_0, ip, tex_output_2);
  }
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`,
      kernelName = `matmul_3_${innerProductLength}`;
    context.addKernel(kernelName, kernelSource);

    if (stridesA[2] > dA.textureWidth || stridesB[1] > dB.textureWidth) {
      throw new Error("MatMul: kernel assumption does not hold");
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_a",
        stridesA,
        dA,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_b",
        stridesB,
        dB,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(resultDims, dC, context.webgl2),
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dA, name: "tex_input_a" },
        { tensor: dB, name: "tex_input_b" },
      ],
      dC,
      uniforms
    );
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "MatMul",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLMatMul(),
    },
  ];
}
