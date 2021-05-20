import { onnx } from "onnx-proto";
import {
  DataArrayConstructor,
  DataType,
} from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrInt } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

// Opset 6+ (opset 1 requires "to" is string)
class Cast extends OperatorImpl {
  to!: onnx.TensorProto.DataType;

  constructor() {
    super("cpu");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.to = getAttrInt(attribute, "to", onnx.TensorProto.DataType.FLOAT);
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    // TODO: コピー回避
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    let outputDataType: DataType;
    switch (this.to) {
      case onnx.TensorProto.DataType.FLOAT:
        outputDataType = "float32";
        break;
      case onnx.TensorProto.DataType.INT32:
      case onnx.TensorProto.DataType.INT64:
        outputDataType = "int32";
        break;
      default:
        throw new Error(
          `Cast: converting to DataType ${this.to} is not yet supported`
        );
    }
    const newData = new DataArrayConstructor[outputDataType](input.data.length);
    newData.set(input.data);
    const output = context.emptyTensor(input.dims, outputDataType, newData);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    { opType: "Cast", backend: "cpu", opsetMin: 6, factory: () => new Cast() },
  ];
}
