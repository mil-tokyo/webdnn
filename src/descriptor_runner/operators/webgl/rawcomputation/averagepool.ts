import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../interface/backend/webgl/webglContext";
import { WebGLTensor } from "../../../interface/backend/webgl/webglTensor";
import {
  shaderGenHeader,
  shaderGenTensorOutputUniform,
  shaderGenTensorNDGet,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenOutput,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputUniformItem,
} from "../shaderHelper";

export async function averagepool(
  context: WebDNNWebGLContext,
  dX: WebGLTensor,
  dI: WebGLTensor,
  countIncludePad: boolean,
  batch: number,
  kernelShape: number[],
  pads: number[],
  strides: number[],
  inShape: number[],
  outShape: number[],
  ch: number
): Promise<void> {
  // ループ回数は定数が必要
  const kernelName = `averagepool_${kernelShape[0]}_${kernelShape[1]}_${countIncludePad}`;
  if (!context.hasKernel(kernelName)) {
    const kernelSource = `${shaderGenHeader(context.webgl2)}

    #define K0 ${kernelShape[0]}
    #define K1 ${kernelShape[1]}
    uniform int CH;
    uniform int S0;
    uniform int S1;
    uniform int P0;
    uniform int P1;
    uniform int IS0;
    uniform int IS1;
    ${shaderGenTensorOutputUniform(4)}
    
    ${shaderGenTensorNDGet("tex_input", 4, context.webgl2)}
    
    void main() {
    ${shaderGenTensorOutputCoordsWithReturn(4)}
    float s = 0.0;
    ${countIncludePad ? "const float c = float(K0 * K1);" : "float c = 0.0;"}
    for (int k0 = 0; k0 < K0; k0++) {
      for (int k1 = 0; k1 < K1; k1++) {
        int in0 = tex_output_2 * S0 - P0 + k0;
        int in1 = tex_output_3 * S1 - P1 + k1;
        if (in0 >= 0 && in0 < IS0 && in1 >= 0 && in1 < IS1) {
          s += get_tex_input(tex_output_0, tex_output_1, in0, in1);
          ${countIncludePad ? "" : "c++;"}
        }
      }
    }
    ${shaderGenOutput("s / c", context.webgl2)}
    return;
    }
    `;
    context.addKernel(kernelName, kernelSource);
  }

  const uniforms: WebGLUniformItem[] = [
    ...shaderGenTensorNDGetUniformItem(
      "tex_input",
      dX.strides,
      dX,
      context.webgl2
    ),
    ...shaderGenTensorOutputUniformItem(dI.dims, dI, context.webgl2),
    { name: "CH", type: "int", value: ch },
    { name: "S0", type: "int", value: strides[0] },
    { name: "S1", type: "int", value: strides[1] },
    { name: "P0", type: "int", value: pads[0] },
    { name: "P1", type: "int", value: pads[1] },
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
