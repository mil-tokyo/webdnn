import { onnx } from "onnx-proto";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInts } from "../operatorUtil";
import { Tensor } from "../../interface/core/tensor";
import { CPUTensor } from "../..";

abstract class Unsqueeze extends OperatorImpl {
  protected calcShapeBase(
    inputShape: ReadonlyArray<number>,
    axes: ReadonlyArray<number>
  ): number[] {
    const expandedNdim = inputShape.length + axes.length;
    const expandedShape: number[] = [];
    let srcIdx = 0;
    const nonNegativeAxes = axes.map((a) => (a >= 0 ? a : a + expandedNdim));
    for (let d = 0; d < expandedNdim; d++) {
      if (nonNegativeAxes.includes(d)) {
        expandedShape.push(1);
      } else {
        expandedShape.push(inputShape[srcIdx++]);
      }
    }
    return expandedShape;
  }
}

export abstract class Unsqueeze1 extends Unsqueeze {
  axes!: number[];

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axes = getAttrInts(attribute, "axes", []);
  }

  protected calcShape(input: Tensor): number[] {
    return this.calcShapeBase(input.dims, this.axes);
  }
}

export abstract class Unsqueeze13 extends Unsqueeze {
  protected calcShape(input: Tensor, axes: CPUTensor): number[] {
    return this.calcShapeBase(input.dims, Array.from(axes.data));
  }
}
