import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrInt, getAttrInts } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

// opset 1
class ReduceMean extends OperatorImpl {
  axes!: number[];
  keepdims!: boolean;

  constructor() {
    super("cpu");
  }
  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axes = getAttrInts(attribute, "axes", []);
    this.keepdims = getAttrInt(attribute, "keepdims", 1) !== 0;
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
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
    const dI = input.data;
    const dO = output.data;
    for (let outer = 0; outer < outerLength; outer++) {
      let s = 0;
      for (let r = 0; r < reductionLength; r++) {
        s += dI[outer * reductionLength + r];
      }
      dO[outer] = s / reductionLength;
    }
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "ReduceMean",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new ReduceMean(),
    },
  ];
}
