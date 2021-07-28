import { onnx } from "onnx-proto";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInts } from "../operatorUtil";
import { Tensor } from "../../interface/core/tensor";
import { CPUTensor } from "../..";

abstract class Squeeze extends OperatorImpl {
  protected calcShapeBase(
    inputShape: ReadonlyArray<number>,
    axes: ReadonlyArray<number>
  ): number[] {
    if (axes.length === 0) {
      // remove all dimensions of 1
      return inputShape.filter((s) => s !== 1);
    } else {
      const nonNegativeAxes = axes.map((a) =>
        a >= 0 ? a : a + inputShape.length
      );
      return inputShape.filter((_, i) => !nonNegativeAxes.includes(i));
    }
  }
}

export abstract class Squeeze1 extends Squeeze {
  axes!: number[];

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axes = getAttrInts(attribute, "axes", []);
  }

  protected calcShape(input: Tensor): number[] {
    return this.calcShapeBase(input.dims, this.axes);
  }
}

export abstract class Squeeze13 extends Squeeze {
  protected calcShape(input: Tensor, axes?: CPUTensor): number[] {
    return this.calcShapeBase(input.dims, axes ? Array.from(axes.data) : []);
  }
}
