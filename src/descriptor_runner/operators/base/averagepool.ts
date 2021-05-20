import { onnx } from "onnx-proto";
import { Backend } from "../../interface/core/constants";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInt, getAttrInts } from "../operatorUtil";

// Version 11
export abstract class AveragePool extends OperatorImpl {
  ceilMode!: boolean;

  countIncludePad!: boolean;

  kernelShape!: number[]; // [y, x]

  pads!: number[]; // [y_begin, x_begin, y_end, x_end]

  strides!: number[]; // [y, x]

  constructor(backend: Backend) {
    super(backend);
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.ceilMode = getAttrInt(attribute, "ceil_mode", 0) !== 0;
    this.countIncludePad = getAttrInt(attribute, "count_include_pad", 0) !== 0;
    this.kernelShape = getAttrInts(attribute, "kernel_shape", []);
    this.pads = getAttrInts(attribute, "pads", []);
    this.strides = getAttrInts(attribute, "strides", []);
  }

  protected calcShape(dimsX: ReadonlyArray<number>) {
    const batch = dimsX[0],
      { kernelShape } = this,
      pads = this.pads.length > 0 ? this.pads : [0, 0, 0, 0],
      strides = this.strides.length > 0 ? this.strides : [1, 1],
      inShape = [dimsX[2], dimsX[3]];
    let outShape: number[];
    if (this.ceilMode) {
      outShape = [
        Math.ceil(
          (inShape[0] + pads[0] + pads[2] - kernelShape[0]) / strides[0]
        ) + 1,
        Math.ceil(
          (inShape[1] + pads[1] + pads[3] - kernelShape[1]) / strides[1]
        ) + 1,
      ];
    } else {
      outShape = [
        Math.floor(
          (inShape[0] + pads[0] + pads[2] - kernelShape[0]) / strides[0]
        ) + 1,
        Math.floor(
          (inShape[1] + pads[1] + pads[3] - kernelShape[1]) / strides[1]
        ) + 1,
      ];
    }
    const ch = dimsX[1];
    return {
      batch,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      ch,
    };
  }
}
