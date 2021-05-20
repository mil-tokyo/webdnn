import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { MaxPool } from "../../../base/maxpool";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";

// Version 11
export class WebGLMaxPool extends MaxPool {
  constructor() {
    super("webgl");
  }

  async run(
    context: WebDNNWebGLContext,
    inputs: Tensor[],
    nOutputs: number
  ): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const inputX = inputs[0];
    if (nOutputs !== 1) {
      // TODO: Indicesの出力対応
      throw new Error("MaxPool: output indices is not yet supported");
    }
    // TODO: 2D以外対応
    if (inputX.ndim !== 4) {
      throw new Error("MaxPool other than 2D is not yet supported");
    }
    if (inputX.dimPerPixel !== 1) {
      throw new Error();
    }

    const {
        batch,
        dilations,
        kernelShape,
        pads,
        strides,
        inShape,
        outShape,
        ch,
      } = this.calcShape(inputX.dims),
      output = context.emptyTensor(
        [batch, ch, outShape[0], outShape[1]],
        "float32",
        1
      ),
      // ループ回数は定数が必要
      kernelName = `maxpool_${kernelShape[0]}_${kernelShape[1]}`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

#define K0 ${kernelShape[0]}
#define K1 ${kernelShape[1]}
uniform int CH;
uniform int S0;
uniform int S1;
uniform int P0;
uniform int P1;
uniform int D0;
uniform int D1;
uniform int IS0;
uniform int IS1;
${shaderGenTensorOutputUniform(4)}

${shaderGenTensorNDGet("tex_input", 4, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(4)}
  float s = -65536.0;
  for (int k0 = 0; k0 < K0; k0++) {
    for (int k1 = 0; k1 < K1; k1++) {
      int in0 = tex_output_2 * S0 - P0 + k0 * D0;
      int in1 = tex_output_3 * S1 - P1 + k1 * D1;
      if (in0 >= 0 && in0 < IS0 && in1 >= 0 && in1 < IS1) {
        float v = get_tex_input(tex_output_0, tex_output_1, in0, in1);
        if (v > s) {
          s = v;
        }
      }
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
        inputX.strides,
        inputX,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(output.dims, output, context.webgl2),
      { name: "CH", type: "int", value: ch },
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
      [{ tensor: inputX, name: "tex_input" }],
      output,
      uniforms
    );
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "MaxPool",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLMaxPool(),
    },
  ];
}
