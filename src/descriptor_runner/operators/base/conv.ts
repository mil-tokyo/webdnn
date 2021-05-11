import { onnx } from "onnx-proto";
import { Backend } from "../../interface/core/constants";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInt, getAttrInts } from "../operatorUtil";

// version 11
export abstract class Conv extends OperatorImpl {
  dilations!: number[]; //[y, x]
  group!: number;
  kernelShape!: number[]; //[y, x]
  pads!: number[]; // [y_begin, x_begin, y_end, x_end]
  strides!: number[]; //[y, x]

  constructor(backend: Backend) {
    super(backend);
  }
  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.dilations = getAttrInts(attribute, "dilations", []);
    this.group = getAttrInt(attribute, "group", 1);
    this.kernelShape = getAttrInts(attribute, "kernel_shape", []);
    this.pads = getAttrInts(attribute, "pads", []);
    this.strides = getAttrInts(attribute, "strides", []);
  }

  protected calcShape(
    dimsX: ReadonlyArray<number>,
    dimsW: ReadonlyArray<number>
  ) {
    const batch = dimsX[0];
    const dilations = this.dilations.length > 0 ? this.dilations : [1, 1];
    const group = this.group;
    const kernelShape =
      this.kernelShape.length > 0 ? this.kernelShape : [dimsW[2], dimsW[3]];
    const pads = this.pads.length > 0 ? this.pads : [0, 0, 0, 0];
    const strides = this.strides.length > 0 ? this.strides : [1, 1];

    const inShape = [dimsX[2], dimsX[3]];
    const outShape = [
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
    const chIn = dimsX[1];
    const chInPerGroup = chIn / group;
    const chOut = dimsW[0];
    const chOutPerGroup = chOut / group;
    return {
      batch,
      dilations,
      group,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      chIn,
      chInPerGroup,
      chOut,
      chOutPerGroup,
    };
  }
}
