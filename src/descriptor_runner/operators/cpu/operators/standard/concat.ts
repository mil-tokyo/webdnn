import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { arrayProd, getAttrInt } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { CPUTensor } from "../../../../interface/backend/cpu/cpuTensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class Concat extends OperatorImpl {
  axis!: number; // 負の場合は後ろから

  constructor() {
    super("cpu");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axis = getAttrInt(attribute, "axis", 0);
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const axis = this.axis >= 0 ? this.axis : inputs[0].ndim + this.axis;
    if (axis < 0 || axis >= inputs[0].ndim) {
      throw new Error(`Concat: axis ${axis} out of range`);
    }
    const inTensors: [CPUTensor, number, number, number, number, number][] = [];
    let axisLength = 0;
    for (let i = 0; i < inputs.length; i++) {
      const it = inputs[i],
        dim = it.dims[axis],
        outerStride = it.strides[Math.max(axis - 1, 0)],
        concatStride = it.strides[axis],
        innerStride = 1;
      inTensors.push([
        it,
        axisLength,
        dim,
        outerStride,
        concatStride,
        innerStride,
      ]);
      axisLength += dim;
    }
    const outputShape = inputs[0].dims.slice();
    outputShape[axis] = axisLength;
    const outerLength = arrayProd(inputs[0].dims.slice(0, axis)),
      innerLength = arrayProd(inputs[0].dims.slice(axis + 1)),
      output = context.emptyTensor(outputShape, inputs[0].dataType),
      outOuterStride = output.strides[Math.max(axis - 1, 0)],
      outConcatStride = output.strides[axis],
      outInnerStride = 1;
    for (const [
      it,
      itAxisOffset,
      itAxisDim,
      outerStride,
      concatStride,
      innerStride,
    ] of inTensors) {
      for (let c = 0; c < itAxisDim; c++) {
        for (let outer = 0; outer < outerLength; outer++) {
          for (let inner = 0; inner < innerLength; inner++) {
            output.data[
              (c + itAxisOffset) * outConcatStride +
                outer * outOuterStride +
                inner * outInnerStride
            ] =
              it.data[
                c * concatStride + outer * outerStride + inner * innerStride
              ];
          }
        }
      }
    }
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Concat",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new Concat(),
    },
  ];
}
