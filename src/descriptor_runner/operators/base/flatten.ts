import { OperatorImpl } from "../operatorImpl";
import { Tensor } from "../../interface/core/tensor";
import { arrayProd, getAttrInt } from "../operatorUtil";
import { onnx } from "onnx-proto";

export abstract class Flatten extends OperatorImpl {
  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    const axis = getAttrInt(attribute, "axis", 1);
    if (axis !== 1) {
      throw new Error(`Flatten: only axis === 1 is supported`);
    }
  }

  protected calcShape(input: Tensor): number[] {
    return [input.dims[0], arrayProd(input.dims.slice(1))];
  }
}
