import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { getAttrInt, getAttrInts } from "../../../operatorUtil";
import {
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
  shaderGenHeader,
} from "../../shaderHelper";
import { OperatorEntry } from "../../../../interface/core/operator";

// opset 1
export class ReduceMean extends OperatorImpl {
  axes!: number[];
  keepdims!: boolean;

  constructor() {
    super("webgl");
  }
  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axes = getAttrInts(attribute, "axes", []);
    this.keepdims = getAttrInt(attribute, "keepdims", 1) !== 0;
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0];
    if (this.axes.length !== 1) {
      throw new Error(`ReduceMean: only single axis is supported`);
    }
    let axis = this.axes[0];
    if (axis < 0) {
      axis += input.ndim;
    }
    if (axis !== input.ndim - 1) {
      throw new Error(
        "ReduceMean: currently only reducing final axis is supported"
      );
    }
    // 最終軸のreductionに特化した実装
    const reductionLength = input.dims[axis];
    const outerLength = input.length / reductionLength;
    const outShape = input.dims.slice();
    if (this.keepdims) {
      outShape[axis] = 1;
    } else {
      outShape.pop();
    }
    const output = context.emptyTensor(outShape, input.dataType);
    const kernelName = `reducemean_${reductionLength}`;
    const kernelSource = `${shaderGenHeader(context.webgl2)}

#define reductionLength ${reductionLength}
#define reductionMul ${1 / reductionLength}
${shaderGenTensorOutputUniform(1)}

${shaderGenTensorNDGet("tex_input", 2, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(1)}
  float s = 0.0;
  for (int i = 0; i < reductionLength; i++) {
    float v = get_tex_input(tex_output_0, i);
    s += v;
  }
  s *= reductionMul;
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
        output,
        context.webgl2
      ),
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
      opType: "ReduceMean",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new ReduceMean(),
    },
  ];
}
