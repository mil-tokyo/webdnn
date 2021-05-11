import { onnx } from "onnx-proto";
import { OperatorImpl } from "../operatorImpl";
import { Tensor } from "../../interface/core/tensor";
import { getAttrInts } from "../operatorUtil";

// opset 1 (13はdifferentiableがついただけ)
export abstract class Transpose extends OperatorImpl {
  perm!: number[];

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.perm = getAttrInts(attribute, "perm", []);
  }

  protected calcShape(input: Tensor): {
    outShape: number[];
    inStrides: number[];
  } {
    // default perm: [ndim-1, ndim-2, ..., 0]
    const perm =
      this.perm.length > 0
        ? this.perm
        : Array.from({ length: input.ndim }, (v, i) => input.ndim - 1 - i);
    if (perm.length !== input.ndim) {
      throw new Error();
    }
    const outShape: number[] = new Array(input.ndim);
    const inStrides: number[] = new Array(input.ndim);
    for (let outAxis = 0; outAxis < input.ndim; outAxis++) {
      const inAxis = perm[outAxis];
      outShape[outAxis] = input.dims[inAxis];
      inStrides[outAxis] = input.strides[inAxis];
    }
    return { outShape, inStrides };
  }
}
