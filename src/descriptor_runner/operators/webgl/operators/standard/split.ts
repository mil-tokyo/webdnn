import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";
import { Split } from "../../../base/split";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { WebGLTensor } from "../../../../interface/backend/webgl/webglTensor";
import { OperatorEntry } from "../../../../interface/core/operator";

/*
 * Opset 2
 * opset 11では区間指定がinputなので互換性なし
 */
export class WebGLSplit extends Split {
  constructor() {
    super("webgl");
  }

  async run(
    context: WebDNNWebGLContext,
    inputs: Tensor[],
    nOutputs: number
  ): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0],
      {
        eachOutputParams,
        outerLength,
        innerLength,
        inOuterStride,
        inConcatStride,
      } = this.calcShape(input, nOutputs),
      outputs: WebGLTensor[] = [],
      kernelName = "split",
      kernelSource = `${shaderGenHeader(context.webgl2)}

${shaderGenTensorOutputUniform(3)}
uniform int offset;

${shaderGenTensorNDGet("tex_input", 3, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(3)}
  float s = get_tex_input(tex_output_0, tex_output_1 + offset, tex_output_2);
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`;
    context.addKernel(kernelName, kernelSource);
    for (let i = 0; i < nOutputs; i++) {
      const { dim, offset, outShape } = eachOutputParams[i],
        ot = context.emptyTensor(outShape, input.dataType),
        uniforms: WebGLUniformItem[] = [
          ...shaderGenTensorNDGetUniformItem(
            "tex_input",
            [inOuterStride, inConcatStride, 1],
            input,
            context.webgl2
          ),
          ...shaderGenTensorOutputUniformItem(
            [outerLength, dim, innerLength],
            ot,
            context.webgl2
          ),
          { name: "offset", type: "int", value: offset },
        ];
      await context.runKernel(
        kernelName,
        [{ tensor: input, name: "tex_input" }],
        ot,
        uniforms
      );
      outputs.push(ot);
    }
    return outputs;
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Split",
      backend: "webgl",
      opsetMin: 1,
      opsetMax: 13,
      factory: () => new WebGLSplit(),
    },
  ];
}
