import { onnx } from "onnx-proto";
import { OperatorImpl } from "../operatorImpl";
import { arrayProd, getAttrInt, getAttrInts } from "../operatorUtil";
import { Tensor } from "../../interface/core/tensor";

// incompatible with opset 13 because it takes "split" as tensor
export abstract class Split extends OperatorImpl {
  axis!: number;
  split!: number[];

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axis = getAttrInt(attribute, "axis", 0);
    this.split = getAttrInts(attribute, "split", []);
  }

  protected calcShape(input: Tensor, nOutputs: number) {
    let axis = this.axis;
    if (axis < 0) {
      axis += input.ndim;
    }
    if (axis < 0 || axis >= input.ndim) {
      throw new Error(`Split: axis ${axis} out of range`);
    }
    const axisLength = input.dims[axis];
    const split =
      this.split.length > 0
        ? this.split
        : Array.from({ length: nOutputs }, () =>
            Math.floor(axisLength / nOutputs)
          );
    const outerLength = arrayProd(input.dims.slice(0, axis));
    const innerLength = arrayProd(input.dims.slice(axis + 1));
    const inOuterStride = input.strides[Math.max(axis - 1, 0)];
    const inConcatStride = input.strides[axis];
    let offset = 0;
    const eachOutputParams: {
      dim: number;
      offset: number;
      outShape: number[];
      outerStride: number;
      splitStride: number;
    }[] = [];
    for (let i = 0; i < nOutputs; i++) {
      const dim = split[i];
      const outShape = input.dims.slice();
      outShape[axis] = dim;
      // stride of output axis=Math.max(axis-1, 0)
      const outerStride = arrayProd(outShape.slice(Math.max(axis - 1, 0) + 1));
      // stride of output axis=axis
      const splitStride = arrayProd(outShape.slice(axis + 1));
      eachOutputParams.push({
        dim,
        offset,
        outShape,
        outerStride,
        splitStride,
      });

      offset += dim;
    }
    return {
      eachOutputParams,
      outerLength,
      innerLength,
      inOuterStride,
      inConcatStride,
    };
  }
}
