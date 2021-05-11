import { onnx } from "onnx-proto";
import { OperatorImpl } from "../operatorImpl";
import { CPUTensor } from "../../interface/backend/cpu/cpuTensor";
import { Tensor } from "../../interface/core/tensor";
import { getAttrInt } from "../operatorUtil";

// opset under 5 takes shape as attribute. not compatible.
export abstract class Reshape5 extends OperatorImpl {
  allowzero!: boolean;

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.allowzero = getAttrInt(attribute, "allowzero", 0) !== 0;
  }

  protected calcShape(input: Tensor, shapeTensor: CPUTensor): number[] {
    const shapeInput = Array.from(shapeTensor.data);

    let computedShape: number[];
    if (this.allowzero) {
      let explicitProd = 1;
      let minusDim = -1;
      shapeInput.forEach((s, i) => {
        if (s > 0) {
          explicitProd *= s;
        } else if (s === -1) {
          if (minusDim >= 0) {
            throw new Error("Reshape: multiple -1 dimensions");
          }
          minusDim = i;
        }
      });
      if (minusDim >= 0 && explicitProd <= 0) {
        throw new Error();
      }
      const minusDimValue = input.length / explicitProd;
      computedShape = shapeInput.map((s) => {
        if (s >= 0) {
          return s;
        } else {
          return minusDimValue;
        }
      });
    } else {
      let explicitProd = 1;
      let minusDim = -1;
      shapeInput.forEach((s, i) => {
        if (s > 0) {
          explicitProd *= s;
        } else if (s === 0) {
          explicitProd *= input.dims[i];
        } else {
          if (s !== -1) {
            throw new Error();
          }
          if (minusDim >= 0) {
            throw new Error("Reshape: multiple -1 dimensions");
          }
          minusDim = i;
        }
      });
      if (minusDim >= 0 && explicitProd <= 0) {
        throw new Error();
      }
      const minusDimValue = input.length / explicitProd;
      computedShape = shapeInput.map((s, i) => {
        if (s > 0) {
          return s;
        } else if (s === 0) {
          return input.dims[i];
        } else {
          return minusDimValue;
        }
      });
    }
    return computedShape;
  }
}
