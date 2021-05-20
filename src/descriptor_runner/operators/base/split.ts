import { onnx } from "onnx-proto";
import { OperatorImpl } from "../operatorImpl";
import { arrayProd, getAttrInt, getAttrInts } from "../operatorUtil";
import { Tensor } from "../../interface/core/tensor";

// Incompatible with opset 13 because it takes "split" as tensor
export abstract class Split extends OperatorImpl {
  axis!: number;

  split!: number[];

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axis = getAttrInt(attribute, "axis", 0);
    this.split = getAttrInts(attribute, "split", []);
  }

  protected calcShape(input: Tensor, nOutputs: number) {
    let { axis } = this;
    if (axis < 0) {
      axis += input.ndim;
    }
    if (axis < 0 || axis >= input.ndim) {
      throw new Error(`Split: axis ${axis} out of range`);
    }
    const axisLength = input.dims[axis],
      split =
        this.split.length > 0
          ? this.split
          : Array.from({ length: nOutputs }, () =>
              Math.floor(axisLength / nOutputs)
            ),
      outerLength = arrayProd(input.dims.slice(0, axis)),
      innerLength = arrayProd(input.dims.slice(axis + 1)),
      inOuterStride = input.strides[Math.max(axis - 1, 0)],
      inConcatStride = input.strides[axis];
    let offset = 0;
    const eachOutputParams: {
      dim: number;
      offset: number;
      outShape: number[];
      outerStride: number;
      splitStride: number;
    }[] = [];
    for (let i = 0; i < nOutputs; i++) {
      const dim = split[i],
        outShape = input.dims.slice();
      outShape[axis] = dim;
      // Stride of output axis=Math.max(axis-1, 0)
      const outerStride = arrayProd(outShape.slice(Math.max(axis - 1, 0) + 1)),
        // Stride of output axis=axis
        splitStride = arrayProd(outShape.slice(axis + 1));
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
