import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { WebGLTensor } from "../../../../interface/backend/webgl/webglTensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Conv } from "../../../base/conv";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";

export class WebGLConv extends Conv {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const inputX = inputs[0],
      inputW = inputs[1],
      inputB = inputs[2];
    // TODO: 2D以外対応
    if (inputX.ndim !== 4) {
      throw new Error("Conv other than 2D is not yet supported");
    }
    const {
      batch,
      dilations,
      group,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      chIn,
      chInPerGroup,
      chOut,
      chOutPerGroup,
    } = this.calcShape(inputX.dims, inputW.dims);
    if (
      inputX.dimPerPixel !== 1 ||
      inputW.dimPerPixel !== 1 ||
      (inputB && inputB.dimPerPixel !== 1)
    ) {
      throw new Error();
    }

    const im2colData = context.emptyTensor([
      group *
        batch *
        outShape[0] *
        outShape[1] *
        chInPerGroup *
        kernelShape[0] *
        kernelShape[1],
    ]);
    await this.im2col(
      context,
      inputX,
      im2colData,
      batch,
      dilations,
      group,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      chIn,
      chInPerGroup,
      chOut,
      chOutPerGroup
    );
    const matmulData = context.emptyTensor([
      group * batch * outShape[0] * outShape[1] * chOutPerGroup,
    ]);
    await this.matmul(
      context,
      im2colData,
      inputW,
      matmulData,
      group,
      batch * outShape[0] * outShape[1],
      chInPerGroup * kernelShape[0] * kernelShape[1],
      chOutPerGroup
    );
    im2colData.dispose();
    const output = context.emptyTensor([
      batch,
      chOut,
      outShape[0],
      outShape[1],
    ]);
    if (inputB) {
      const transposeData = context.emptyTensor([
        batch * chOut * outShape[0] * outShape[1],
      ]);

      await this.transpose(
        context,
        matmulData,
        transposeData,
        group,
        batch,
        outShape[0] * outShape[1],
        chOutPerGroup
      );
      matmulData.dispose();
      await this.bias(
        context,
        transposeData,
        inputB,
        output,
        batch,
        chOut,
        outShape[0] * outShape[1]
      );
      transposeData.dispose();
    } else {
      await this.transpose(
        context,
        matmulData,
        output,
        group,
        batch,
        outShape[0] * outShape[1],
        chOutPerGroup
      );
      matmulData.dispose();
    }
    return [output];
  }

  private async im2col(
    context: WebDNNWebGLContext,
    dX: WebGLTensor,
    dI: WebGLTensor,
    batch: number,
    dilations: number[],
    group: number,
    kernelShape: number[],
    pads: number[],
    strides: number[],
    inShape: number[],
    outShape: number[],
    chIn: number,
    chInPerGroup: number,
    chOut: number,
    chOutPerGroup: number
  ) {
    const kernelName = `conv_im2col`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  uniform int GROUP;
  uniform int BATCH;
  uniform int O0;
  uniform int O1;
  uniform int CI;
  uniform int CIPG;
  uniform int K0;
  uniform int K1;
  uniform int S0;
  uniform int S1;
  uniform int P0;
  uniform int P1;
  uniform int D0;
  uniform int D1;
  uniform int IS0;
  uniform int IS1;
  
  ${shaderGenTensorNDGet("tex_input", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / K0;
    int k1 = rem - quo * K1;
    rem = quo;
    quo = rem / K0;
    int k0 = rem - quo * K0;
    rem = quo;
    quo = rem / CIPG;
    int ci = rem - quo * CIPG;
    rem = quo;
    quo = rem / O1;
    int o1 = rem - quo * O1;
    rem = quo;
    quo = rem / O0;
    int o0 = rem - quo * O0;
    rem = quo;
    quo = rem / BATCH;
    int b = rem - quo * BATCH;
    int g = quo;
  
    int in0 = o0 * S0 - P0 + k0 * D0;
    int in1 = o1 * S1 - P1 + k1 * D1;
    float s = 0.0;
    if (in0 >= 0 && in0 < IS0 && in1 >= 0 && in1 < IS1) {
      s = get_tex_input(((b * CI + g * CIPG + ci) * IS0 + in0) * IS1 + in1);
    }
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem("tex_input", [1], dX, context.webgl2),
      ...shaderGenTensorOutputUniformItem([dI.length], dI, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BATCH", type: "int", value: batch },
      { name: "O0", type: "int", value: outShape[0] },
      { name: "O1", type: "int", value: outShape[1] },
      { name: "CI", type: "int", value: chIn },
      { name: "CIPG", type: "int", value: chInPerGroup },
      { name: "K0", type: "int", value: kernelShape[0] },
      { name: "K1", type: "int", value: kernelShape[1] },
      { name: "S0", type: "int", value: strides[0] },
      { name: "S1", type: "int", value: strides[1] },
      { name: "P0", type: "int", value: pads[0] },
      { name: "P1", type: "int", value: pads[1] },
      { name: "D0", type: "int", value: dilations[0] },
      { name: "D1", type: "int", value: dilations[1] },
      { name: "IS0", type: "int", value: inShape[0] },
      { name: "IS1", type: "int", value: inShape[1] },
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dX, name: "tex_input" }],
      dI,
      uniforms
    );
  }

  private async matmul(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dW: WebGLTensor,
    dT: WebGLTensor,
    group: number,
    bout: number,
    cinkhkw: number,
    chOutPerGroup: number
  ) {
    /*
     * DI(group, bout, cinkhkw) * dW(group, coutpergroup, cinkhkw) -> dT(group, bout, coutpergroup)
     * ループ回数は定数が必要
     */
    const kernelName = `conv_matmul_${cinkhkw}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  #define cinkhkw ${cinkhkw}
  uniform int GROUP;
  uniform int BOUT;
  uniform int COPG;
  
  ${shaderGenTensorNDGet("tex_input_w", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / COPG;
    int x = rem - quo * COPG;
    rem = quo;
    quo = rem / BOUT;
    int y = rem - quo * BOUT;
    int g = quo;
  
    float s = 0.0;
    for (int ip = 0; ip < cinkhkw; ip++) {
      s += get_tex_input_i((g * BOUT + y) * cinkhkw + ip) * get_tex_input_w((g * COPG + x) * cinkhkw + ip);
    }
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_w",
        [1],
        dW,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dI,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dT.length], dT, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BOUT", type: "int", value: bout },
      { name: "COPG", type: "int", value: chOutPerGroup },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dW, name: "tex_input_w" },
        { tensor: dI, name: "tex_input_i" },
      ],
      dT,
      uniforms
    );
  }

  private async transpose(
    context: WebDNNWebGLContext,
    dT: WebGLTensor,
    dO: WebGLTensor,
    group: number,
    batch: number,
    outarea: number,
    chOutPerGroup: number
  ) {
    // DT(group, batch, outh, outw, choutpergroup) -> dO(batch, group, choutpergroup, outh, outw)

    const kernelName = `conv_transpose`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  uniform int GROUP;
  uniform int BATCH;
  uniform int COPG;
  uniform int OUTAREA;
  
  ${shaderGenTensorNDGet("tex_input", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / OUTAREA;
    int x = rem - quo * OUTAREA;
    rem = quo;
    quo = rem / COPG;
    int c = rem - quo * COPG;
    rem = quo;
    quo = rem / GROUP;
    int g = rem - quo * GROUP;
    int b = quo;
  
    float s = 0.0;
    s = get_tex_input(((g * BATCH + b) * OUTAREA + x) * COPG + c);
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem("tex_input", [1], dT, context.webgl2),
      ...shaderGenTensorOutputUniformItem([dO.length], dO, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BATCH", type: "int", value: batch },
      { name: "COPG", type: "int", value: chOutPerGroup },
      { name: "OUTAREA", type: "int", value: outarea },
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dT, name: "tex_input" }],
      dO,
      uniforms
    );
  }

  private async bias(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dB: WebGLTensor,
    dO: WebGLTensor,
    batch: number,
    chOut: number,
    outarea: number
  ) {
    const kernelName = `conv_bias`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  uniform int BATCH;
  uniform int COUT;
  uniform int OUTAREA;
  
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_b", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / OUTAREA;
    int x = rem - quo * OUTAREA;
    rem = quo;
    quo = rem / COUT;
    int c = rem - quo * COUT;
    int b = quo;
  
    float s = 0.0;
    s = get_tex_input_i(tex_output_flat) + get_tex_input_b(c);
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dI,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_b",
        [1],
        dB,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dO.length], dO, context.webgl2),
      { name: "BATCH", type: "int", value: batch },
      { name: "COUT", type: "int", value: chOut },
      { name: "OUTAREA", type: "int", value: outarea },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dI, name: "tex_input_i" },
        { tensor: dB, name: "tex_input_b" },
      ],
      dO,
      uniforms
    );
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Conv",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLConv(),
    },
  ];
}
