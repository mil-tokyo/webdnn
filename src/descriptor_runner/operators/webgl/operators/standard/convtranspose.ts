import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { WebGLTensor } from "../../../../interface/backend/webgl/webglTensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { ConvTranspose } from "../../../base/convtranspose";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";

export class WebGLConvTranspose extends ConvTranspose {
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
      throw new Error("ConvTranspose other than 2D is not yet supported");
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
    const inputTransposeData = context.emptyTensor([
      chIn * batch * inShape[0] * inShape[1],
    ]);
    await this.transposeInput(
      context,
      inputX,
      inputTransposeData,
      group,
      batch,
      inShape[0] * inShape[1],
      chInPerGroup
    );
    const weightTransposeData = context.emptyTensor([
      chOut * kernelShape[0] * kernelShape[1] * chInPerGroup,
    ]);
    await this.transposeWeight(
      context,
      inputW,
      weightTransposeData,
      group,
      chInPerGroup,
      chOutPerGroup,
      kernelShape[0] * kernelShape[1]
    );
    const matmulData = context.emptyTensor([
      chOut * batch * inShape[0] * inShape[1] * kernelShape[0] * kernelShape[1],
    ]);
    await this.matmul(
      context,
      inputTransposeData,
      weightTransposeData,
      matmulData,
      group,
      batch * inShape[0] * inShape[1],
      chOutPerGroup * kernelShape[0] * kernelShape[1],
      chInPerGroup
    );
    inputTransposeData.dispose();
    weightTransposeData.dispose();
    const output = context.emptyTensor([
      batch,
      chOut,
      outShape[0],
      outShape[1],
    ]);

    if (inputB) {
      const col2ImData = context.emptyTensor([
        batch * chOut * outShape[0] * outShape[1],
      ]);
      await this.col2im(
        context,
        matmulData,
        col2ImData,
        batch,
        dilations,
        group,
        kernelShape,
        pads,
        strides,
        inShape,
        outShape,
        chOutPerGroup
      );
      matmulData.dispose();
      await this.bias(
        context,
        col2ImData,
        inputB,
        output,
        batch,
        chOut,
        outShape[0] * outShape[1]
      );
      col2ImData.dispose();
    } else {
      await this.col2im(
        context,
        matmulData,
        output,
        batch,
        dilations,
        group,
        kernelShape,
        pads,
        strides,
        inShape,
        outShape,
        chOutPerGroup
      );
      matmulData.dispose();
    }
    return [output];
  }

  private async col2im(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dY: WebGLTensor,
    batch: number,
    dilations: number[],
    group: number,
    kernelShape: number[],
    pads: number[],
    strides: number[],
    inShape: number[],
    outShape: number[],
    chOutPerGroup: number
  ) {
    // dI: group, batch, inShape[0], inShape[1], chOutPerGroup, kernelShape[0], kernelShape[1]
    // dY: batch, group, chOutPerGroup, outShape[0], outShape[1]
    const kernelName = `convtranspose_col2im_${kernelShape[0]}_${kernelShape[1]}_${strides[0]}_${strides[1]}_${pads[0]}_${pads[1]}_${dilations[0]}_${dilations[1]}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  #define K0 ${kernelShape[0]}
  #define K1 ${kernelShape[1]}
  #define S0 ${strides[0]}
  #define S1 ${strides[1]}
  #define P0 ${pads[0]}
  #define P1 ${pads[1]}
  #define D0 ${dilations[0]}
  #define D1 ${dilations[1]}
  uniform int GROUP;
  uniform int BATCH;
  uniform int O0;
  uniform int O1;
  uniform int COPG;
  uniform int IS0;
  uniform int IS1;
  
  ${shaderGenTensorNDGet("tex_input", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / O1;
    int o1 = rem - quo * O1;
    rem = quo;
    quo = rem / O0;
    int o0 = rem - quo * O0;
    rem = quo;
    quo = rem / COPG;
    int co = rem - quo * COPG;
    rem = quo;
    quo = rem / GROUP;
    int g = rem - quo * GROUP;
    int b = quo;
  
    float s = 0.0;
    for (int k0 = 0; k0 < K0; k0++) {
      for (int k1 = 0; k1 < K1; k1++) {
        int i0s = o0 + P0 - k0 * D0;
        int i1s = o1 + P1 - k1 * D1;
        int i0 = i0s / S0;
        if (i0s - i0 * S0 != 0 || i0 < 0 || i0 >= IS0) {
          continue;
        }
        int i1 = i1s / S1;
        if (i1s - i1 * S1 != 0 || i1 < 0 || i1 >= IS1) {
          continue;
        }
        s += get_tex_input((((((g * BATCH + b) * IS0 + i0) * IS1 + i1) * COPG + co) * K0 + k0) * K1 + k1);
      }
    }
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem("tex_input", [1], dI, context.webgl2),
      ...shaderGenTensorOutputUniformItem([dY.length], dY, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BATCH", type: "int", value: batch },
      { name: "O0", type: "int", value: outShape[0] },
      { name: "O1", type: "int", value: outShape[1] },
      { name: "COPG", type: "int", value: chOutPerGroup },
      { name: "IS0", type: "int", value: inShape[0] },
      { name: "IS1", type: "int", value: inShape[1] },
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dI, name: "tex_input" }],
      dY,
      uniforms
    );
  }

  private async matmul(
    context: WebDNNWebGLContext,
    dTX: WebGLTensor,
    dTW: WebGLTensor,
    dI: WebGLTensor,
    group: number,
    bin: number,
    cks: number,
    chInPerGroup: number
  ) {
    /*
       dTX(group, batch*inShape[0]*inShape[1]=bin, chInPerGroup) * dTW(group, chOutPerGroup*kernelShape[0]*kernelShape[1]=cks, chInPerGroup) -> dI(group, bin, cks)
     * ループ回数は定数が必要
     */
    const kernelName = `convtranspose_matmul_${chInPerGroup}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  #define cipg ${chInPerGroup}
  uniform int GROUP;
  uniform int BIN;
  uniform int CKS;
  
  ${shaderGenTensorNDGet("tex_input_w", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / CKS;
    int x = rem - quo * CKS;
    rem = quo;
    quo = rem / BIN;
    int y = rem - quo * BIN;
    int g = quo;
  
    float s = 0.0;
    for (int ip = 0; ip < cipg; ip++) {
      s += get_tex_input_i((g * BIN + y) * cipg + ip) * get_tex_input_w((g * CKS + x) * cipg + ip);
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
        dTW,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dTX,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dI.length], dI, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BIN", type: "int", value: bin },
      { name: "CKS", type: "int", value: cks },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dTW, name: "tex_input_w" },
        { tensor: dTX, name: "tex_input_i" },
      ],
      dI,
      uniforms
    );
  }

  private async transposeInput(
    context: WebDNNWebGLContext,
    dX: WebGLTensor,
    dTX: WebGLTensor,
    group: number,
    batch: number,
    inarea: number,
    chInPerGroup: number
  ) {
    // dX(batch, group, chInPerGroup, inShape[0], inShape[1]) -> dTX(group, batch, inShape[0], inShape[1], chInPerGroup)
    const kernelName = `convtranspose_transpose_input`;
    const kernelSource = `${shaderGenHeader(context.webgl2)}

${shaderGenTensorOutputUniform(4)}

${shaderGenTensorNDGet("tex_input", 4, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(4)}
  float s = get_tex_input(tex_output_0, tex_output_1, tex_output_2, tex_output_3);
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [chInPerGroup * inarea, group * chInPerGroup * inarea, 1, inarea],
        dX,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [group, batch, inarea, chInPerGroup],
        dTX,
        context.webgl2
      ),
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dX, name: "tex_input" }],
      dTX,
      uniforms
    );
  }

  private async transposeWeight(
    context: WebDNNWebGLContext,
    dW: WebGLTensor,
    dTW: WebGLTensor,
    group: number,
    chInPerGroup: number,
    chOutPerGroup: number,
    karea: number
  ) {
    // dW(group, chInPerGroup, chOutPerGroup, kernelShape[0], kernelShape[1]) -> dTW(group, chOutPerGroup, kernelShape[0], kernelShape[1], cInPerGroup)
    const kernelName = `convtranspose_transpose_weight`;
    const kernelSource = `${shaderGenHeader(context.webgl2)}

${shaderGenTensorOutputUniform(4)}

${shaderGenTensorNDGet("tex_input", 4, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(4)}
  float s = get_tex_input(tex_output_0, tex_output_1, tex_output_2, tex_output_3);
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        [chInPerGroup * chOutPerGroup * karea, karea, 1, chOutPerGroup * karea],
        dW,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        [group, chOutPerGroup, karea, chInPerGroup],
        dTW,
        context.webgl2
      ),
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dW, name: "tex_input" }],
      dTW,
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
    const kernelName = `convtranspose_bias`;
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
      opType: "ConvTranspose",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLConvTranspose(),
    },
  ];
}
