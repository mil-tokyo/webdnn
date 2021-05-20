import { onnx } from "onnx-proto";
import { Backend } from "../../interface/core/constants";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInt, getAttrInts } from "../operatorUtil";

// Version 11
export abstract class Conv extends OperatorImpl {
  dilations!: number[]; // [y, x]

  group!: number;

  kernelShape!: number[]; // [y, x]

  pads!: number[]; // [y_begin, x_begin, y_end, x_end]

  strides!: number[]; // [y, x]

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
    const batch = dimsX[0],
      dilations = this.dilations.length > 0 ? this.dilations : [1, 1],
      { group } = this,
      kernelShape =
        this.kernelShape.length > 0 ? this.kernelShape : [dimsW[2], dimsW[3]],
      pads = this.pads.length > 0 ? this.pads : [0, 0, 0, 0],
      strides = this.strides.length > 0 ? this.strides : [1, 1],
      inShape = [dimsX[2], dimsX[3]],
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
      ],
      chIn = dimsX[1],
      chInPerGroup = chIn / group,
      chOut = dimsW[0],
      chOutPerGroup = chOut / group;
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
