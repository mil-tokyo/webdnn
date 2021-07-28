import { onnx } from "onnx-proto";
import { OperatorImpl } from "../operatorImpl";
import { arrayProd, getAttrInt, getAttrInts } from "../operatorUtil";
import { Tensor } from "../../interface/core/tensor";
import { CPUTensor } from "../..";

abstract class Split extends OperatorImpl {
  axis!: number;

  protected calcShapeBase(
    input: Tensor,
    nOutputs: number,
    splitSrc: ReadonlyArray<number>
  ) {
    let { axis } = this;
    if (axis < 0) {
      axis += input.ndim;
    }
    if (axis < 0 || axis >= input.ndim) {
      throw new Error(`Split: axis ${axis} out of range`);
    }
    const axisLength = input.dims[axis],
      split =
        splitSrc.length > 0
          ? splitSrc
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

export abstract class Split2 extends Split {
  split!: number[];

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axis = getAttrInt(attribute, "axis", 0);
    this.split = getAttrInts(attribute, "split", []);
  }

  protected calcShape(input: Tensor, nOutputs: number) {
    return this.calcShapeBase(input, nOutputs, this.split);
  }
}

export abstract class Split13 extends Split {
  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axis = getAttrInt(attribute, "axis", 0);
  }

  protected calcShape(
    input: Tensor,
    nOutputs: number,
    splitTensor?: CPUTensor
  ) {
    return this.calcShapeBase(
      input,
      nOutputs,
      splitTensor ? Array.from(splitTensor.data) : []
    );
  }
}
