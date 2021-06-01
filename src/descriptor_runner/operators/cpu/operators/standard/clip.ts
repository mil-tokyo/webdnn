import { DataArrayConstructor } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { onnx } from "onnx-proto";
import { getAttrFloat } from "../../../operatorUtil";

class CPUClip extends OperatorImpl {
  clipMax!: number;
  clipMin!: number;

  constructor() {
    super("cpu");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.clipMax = getAttrFloat(attribute, "max", 65536);
    this.clipMin = getAttrFloat(attribute, "min", -65536);
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    if (!["float32"].includes(input.dataType)) {
      throw new Error(`Unary: DataType ${input.dataType} not supported`);
    }
    const newData = new DataArrayConstructor[input.dataType](input.data.length);
    const { clipMax, clipMin } = this;
    for (let i = 0; i < newData.length; i++) {
      newData[i] = Math.min(clipMax, Math.max(input.data[i], clipMin));
    }
    const output = context.emptyTensor(input.dims, input.dataType, newData);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Clip",
      backend: "cpu",
      opsetMin: 1,
      opsetMax: 11,
      factory: () => new CPUClip(),
    },
  ];
}
