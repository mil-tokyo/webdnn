import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { getAttrInt, getAttrInts } from "../../../operatorUtil";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";
import { OperatorEntry } from "../../../../interface/core/operator";

// Opset 1
export class ReduceOp extends OperatorImpl {
  axes!: number[];

  keepdims!: boolean;

  constructor(
    private opType: string,
    private shaderInit: string,
    private shaderAccum: string,
    private shaderOutput: string
  ) {
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
      throw new Error(`${this.opType}: only single axis is supported`);
    }
    let axis = this.axes[0];
    if (axis < 0) {
      axis += input.ndim;
    }
    if (axis !== input.ndim - 1) {
      throw new Error(
        `${this.opType}: currently only reducing final axis is supported`
      );
    }
    // 最終軸のreductionに特化した実装
    const reductionLength = input.dims[axis],
      outerLength = input.length / reductionLength,
      outShape = input.dims.slice();
    if (this.keepdims) {
      outShape[axis] = 1;
    } else {
      outShape.pop();
    }
    const output = context.emptyTensor(outShape, input.dataType),
      kernelName = `reduceop_${this.opType}_${reductionLength}`,
      kernelSource = `${shaderGenHeader(context.webgl2)}

#define reductionLength ${reductionLength}
#define reductionMul ${1 / reductionLength}
${shaderGenTensorOutputUniform(1)}

${shaderGenTensorNDGet("tex_input", 2, context.webgl2)}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(1)}
  float s = ${this.shaderInit}
  for (int i = 0; i < reductionLength; i++) {
    float v = get_tex_input(tex_output_0, i);
    ${this.shaderAccum}
  }
  ${this.shaderOutput}
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
      opType: "ReduceL1",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new ReduceOp("ReduceL1", "0.0;", "s += abs(v);", ""),
    },
    {
      opType: "ReduceL2",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new ReduceOp("ReduceL2", "0.0;", "s += v * v;", "s = sqrt(s);"),
    },
    {
      opType: "ReduceLogSum",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new ReduceOp("ReduceLogSum", "0.0;", "s += v;", "s = log(s);"),
    },
    {
      opType: "ReduceLogSumExp",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new ReduceOp("ReduceLogSumExp", "0.0;", "s += exp(v);", "s = log(s);"),
    },
    {
      opType: "ReduceMax",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new ReduceOp("ReduceMax", "-65536.0;", "if (v > s) { s = v; }", ""),
    },
    {
      opType: "ReduceMean",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new ReduceOp("ReduceMean", "0.0;", "s += v;", "s *= reductionMul;"),
    },
    {
      opType: "ReduceMin",
      backend: "webgl",
      opsetMin: 1,
      factory: () =>
        new ReduceOp("ReduceMin", "65536.0;", "if (v < s) { s = v; }", ""),
    },
    {
      opType: "ReduceProd",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new ReduceOp("ReduceProd", "1.0;", "s *= v;", ""),
    },
    {
      opType: "ReduceSum",
      backend: "webgl",
      opsetMin: 1,
      opsetMax: 13,
      factory: () => new ReduceOp("ReduceSum", "0.0;", "s += v;", ""),
    },
    {
      opType: "ReduceSumSquare",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new ReduceOp("ReduceSumSquare", "0.0;", "s += v * v;", ""),
    },
  ];
}
