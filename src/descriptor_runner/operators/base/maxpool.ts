import { onnx } from "onnx-proto";
import { Backend } from "../../interface/core/constants";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInt, getAttrInts } from "../operatorUtil";

export abstract class MaxPool extends OperatorImpl {
  ceilMode!: boolean;
  dilations!: number[]; //[y, x]
  kernelShape!: number[]; //[y, x]
  pads!: number[]; // [y_begin, x_begin, y_end, x_end]
  strides!: number[]; //[y, x]

  constructor(backend: Backend) {
    super(backend);
  }
  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    // TODO: check auto_pad is 'NOTSET'
    this.ceilMode = getAttrInt(attribute, "ceil_mode", 0) !== 0;
    this.dilations = getAttrInts(attribute, "dilations", []);
    this.kernelShape = getAttrInts(attribute, "kernel_shape", []);
    this.pads = getAttrInts(attribute, "pads", []);
    this.strides = getAttrInts(attribute, "strides", []);
    const storageOrder = getAttrInt(attribute, "storage_order", 0);
    if (storageOrder !== 0) {
      throw new Error(`MaxPool: storage_order !== 0 is not supported.`);
    }
  }

  protected calcShape(dimsX: ReadonlyArray<number>) {
    const batch = dimsX[0];
    const dilations = this.dilations.length > 0 ? this.dilations : [1, 1];
    const kernelShape = this.kernelShape;
    const pads = this.pads.length > 0 ? this.pads : [0, 0, 0, 0];
    const strides = this.strides.length > 0 ? this.strides : [1, 1];

    const inShape = [dimsX[2], dimsX[3]];
    let outShape: number[];
    if (this.ceilMode) {
      outShape = [
        Math.ceil(
          (inShape[0] +
            pads[0] +
            pads[2] -
            dilations[0] * (kernelShape[0] - 1) -
            1) /
            strides[0]
        ) + 1,
        Math.ceil(
          (inShape[1] +
            pads[1] +
            pads[3] -
            dilations[1] * (kernelShape[1] - 1) -
            1) /
            strides[1]
        ) + 1,
      ];
    } else {
      outShape = [
        Math.floor(
          (inShape[0] +
            pads[0] +
            pads[2] -
            dilations[0] * (kernelShape[0] - 1) -
            1) /
            strides[0]
        ) + 1,
        Math.floor(
          (inShape[1] +
            pads[1] +
            pads[3] -
            dilations[1] * (kernelShape[1] - 1) -
            1) /
            strides[1]
        ) + 1,
      ];
    }
    const ch = dimsX[1];
    return {
      batch,
      dilations,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      ch,
    };
  }
}
