import { onnx } from "onnx-proto";
import { Backend } from "../../interface/core/constants";
import { OperatorImpl } from "../operatorImpl";
import { getAttrInt, getAttrInts, getAttrString } from "../operatorUtil";

// Version 11
export abstract class ConvTranspose extends OperatorImpl {
  autoPad!: string;
  dilations!: number[]; // [y, x]
  group!: number;
  kernelShape!: number[]; // [y, x]
  outputPadding!: number[]; // [y, x]
  outputShape!: number[]; // [y, x]
  pads!: number[]; // [y_begin, x_begin, y_end, x_end]
  strides!: number[]; // [y, x]

  constructor(backend: Backend) {
    super(backend);
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.autoPad = getAttrString(attribute, "auto_pad", "NOTSET");
    this.dilations = getAttrInts(attribute, "dilations", []);
    this.group = getAttrInt(attribute, "group", 1);
    this.kernelShape = getAttrInts(attribute, "kernel_shape", []);
    this.outputPadding = getAttrInts(attribute, "output_padding", []);
    this.outputShape = getAttrInts(attribute, "output_shape", []);
    this.pads = getAttrInts(attribute, "pads", []);
    this.strides = getAttrInts(attribute, "strides", []);
  }

  protected calcShape(
    dimsX: ReadonlyArray<number>,
    dimsW: ReadonlyArray<number>
  ) {
    if (this.autoPad !== "NOTSET") {
      throw new Error(
        "ConvTranspose: auto_pad !== NOTSET is not yet supported."
      );
    }
    if (this.outputShape.length > 0) {
      throw new Error(
        "ConvTranspose: explicit output_shape is not yet supported."
      );
    }
    const batch = dimsX[0],
      dilations = this.dilations.length > 0 ? this.dilations : [1, 1],
      { group } = this,
      kernelShape =
        this.kernelShape.length > 0 ? this.kernelShape : [dimsW[2], dimsW[3]],
      pads = this.pads.length > 0 ? this.pads : [0, 0, 0, 0],
      strides = this.strides.length > 0 ? this.strides : [1, 1],
      inShape = [dimsX[2], dimsX[3]],
      outputPadding =
        this.outputPadding.length > 0 ? this.outputPadding : [0, 0],
      outShape = [
        strides[0] * (inShape[0] - 1) +
          outputPadding[0] +
          (kernelShape[0] - 1) * dilations[0] +
          1 -
          pads[0] -
          pads[2],
        strides[1] * (inShape[1] - 1) +
          outputPadding[1] +
          (kernelShape[1] - 1) * dilations[1] +
          1 -
          pads[1] -
          pads[3],
      ],
      chIn = dimsX[1],
      chInPerGroup = chIn / group,
      chOutPerGroup = dimsW[1],
      chOut = chOutPerGroup * group;
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
