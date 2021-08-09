import { onnx } from "onnx-proto";
import { Backend } from "../../interface/core/constants";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInt, getAttrInts, getAttrString } from "../operatorUtil";

// Version 11
export abstract class AveragePool extends OperatorImpl {
  autoPad!: string;
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
    this.autoPad = getAttrString(attribute, "auto_pad", "NOTSET");
    this.ceilMode = getAttrInt(attribute, "ceil_mode", 0) !== 0;
    this.countIncludePad = getAttrInt(attribute, "count_include_pad", 0) !== 0;
    this.kernelShape = getAttrInts(attribute, "kernel_shape", []);
    this.pads = getAttrInts(attribute, "pads", []);
    this.strides = getAttrInts(attribute, "strides", []);
  }

  protected calcShape(dimsX: ReadonlyArray<number>) {
    const batch = dimsX[0],
      { kernelShape } = this,
      strides = this.strides.length > 0 ? this.strides : [1, 1],
      inShape = [dimsX[2], dimsX[3]];
    let outShape: number[];
    let pads: number[];
    if (this.autoPad === "NOTSET") {
      pads = this.pads.length > 0 ? this.pads : [0, 0, 0, 0];
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
    } else if (this.autoPad === "SAME_UPPER" || this.autoPad === "SAME_LOWER") {
      // calculate output shape as if padding is zero
      outShape = [
        Math.ceil(inShape[0] / strides[0]),
        Math.ceil(inShape[1] / strides[1]),
      ];
      // calculate needed padding
      const sumPad = [
        (outShape[0] - 1) * strides[0] + kernelShape[0] - inShape[0],
        (outShape[1] - 1) * strides[1] + kernelShape[1] - inShape[1],
      ];
      if (this.autoPad === "SAME_UPPER") {
        pads = [
          Math.floor(sumPad[0] / 2),
          Math.floor(sumPad[1] / 2),
          Math.ceil(sumPad[0] / 2),
          Math.ceil(sumPad[1] / 2),
        ];
      } else if (this.autoPad === "SAME_LOWER") {
        pads = [
          Math.ceil(sumPad[0] / 2),
          Math.ceil(sumPad[1] / 2),
          Math.floor(sumPad[0] / 2),
          Math.floor(sumPad[1] / 2),
        ];
      } else {
        throw new Error();
      }
    } else if (this.autoPad === "VALID") {
      outShape = [
        Math.ceil((inShape[0] - kernelShape[0] + 1) / strides[0]),
        Math.ceil((inShape[1] - kernelShape[1] + 1) / strides[1]),
      ];
      pads = [0, 0, 0, 0];
    } else {
      throw new Error(`Unknown auto_pad ${this.autoPad} for AveragePool`);
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
