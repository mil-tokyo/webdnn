import { onnx } from "onnx-proto";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInts } from "../operatorUtil";
import { Tensor } from "../../interface/core/tensor";

/*
 * Opset 1
 * opset 11以降はaxesがinputとして与えられるため非互換(また、負の軸も許容)
 */
export abstract class Unsqueeze extends OperatorImpl {
  axes!: number[];

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axes = getAttrInts(attribute, "axes", []);
  }

  protected calcShape(input: Tensor): number[] {
    if (this.axes.length > 1) {
      throw new Error(`Unsqueeze: multiple axes is not yet supported`);
      // サポートするときは挿入順序に注意
    }
    const newShape = input.dims.slice();
    newShape.splice(this.axes[0], 0, 1);
    return newShape;
  }
}
