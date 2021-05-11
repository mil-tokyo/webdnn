import {
  shaderGenHeader,
  shaderGenTensorOutputUniform,
  shaderGenTensorNDGet,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenOutput,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";
import { Transpose } from "../../../base/transpose";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

// version 11
export class WebGLTranspose extends Transpose {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0];
    if (input.dataType !== "float32") {
      throw new Error();
    }
    if (input.dimPerPixel !== 1) {
      throw new Error();
    }
    const { outShape, inStrides } = this.calcShape(input);

    const output = context.emptyTensor(outShape, "float32", 1);
    const kernelName = `transpose_${outShape.length}`;
    let tex_input_idxs: string;
    switch (inStrides.length) {
      case 0:
        tex_input_idxs = "";
        break;
      case 1:
        tex_input_idxs = "tex_output_0";
        break;
      case 2:
        tex_input_idxs = "tex_output_0, tex_output_1";
        break;
      case 3:
        tex_input_idxs = "tex_output_0, tex_output_1, tex_output_2";
        break;
      case 4:
        tex_input_idxs =
          "tex_output_0, tex_output_1, tex_output_2, tex_output_3";
        break;
      default:
        throw new Error("Input with more than 4 dimensions is not supported");
    }
    const kernelSource = `${shaderGenHeader(context.webgl2)}

${shaderGenTensorOutputUniform(outShape.length)}

${shaderGenTensorNDGet("tex_input", inStrides.length, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(outShape.length)}
  float s = get_tex_input(${tex_input_idxs});
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        inStrides,
        input,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(outShape, output, context.webgl2),
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: input, name: "tex_input" }],
      output,
      uniforms
    );
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Transpose",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLTranspose(),
    },
  ];
}
