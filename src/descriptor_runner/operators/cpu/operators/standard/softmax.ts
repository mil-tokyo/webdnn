import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrInt } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class Softmax extends OperatorImpl {
  axis!: number;

  constructor() {
    super("cpu");
  }
  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    // TODO: support axis, whose default is different between opsets
    this.axis = getAttrInt(attribute, "axis", -1);
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    let axis = this.axis;
    if (axis < 0) {
      axis += input.ndim;
    }
    if (axis !== input.ndim - 1) {
      throw new Error(
        "Softmax: currently only reducing final axis is supported"
      );
    }
    // 最終軸のreductionに特化した実装
    const reductionLength = input.dims[axis];
    const outerLength = input.length / reductionLength;
    const output = context.emptyTensor(input.dims, input.dataType);
    const dI = input.data;
    const dO = output.data;
    for (let outer = 0; outer < outerLength; outer++) {
      let max = -Infinity;
      for (let r = 0; r < reductionLength; r++) {
        const v = dI[outer * reductionLength + r];
        if (v > max) {
          max = v;
        }
      }
      let expsum = 0;
      for (let r = 0; r < reductionLength; r++) {
        const v = dI[outer * reductionLength + r];
        const exp = Math.exp(v - max);
        dO[outer * reductionLength + r] = exp;
        expsum += exp;
      }
      for (let r = 0; r < reductionLength; r++) {
        dO[outer * reductionLength + r] /= expsum;
      }
    }
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Softmax",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new Softmax(),
    },
  ];
}
