import { onnx } from "onnx-proto";
import {
  DataArrayConstructor,
  DataType,
} from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { getAttrFloat } from "../../../operatorUtil";

class LeakyRelu extends OperatorImpl {
  private allowDataTypes: DataType[];
  alpha!: number;

  constructor() {
    super("cpu");
    this.allowDataTypes = ["float32"];
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.alpha = getAttrFloat(attribute, "alpha", 0.01);
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    if (!this.allowDataTypes.includes(input.dataType)) {
      throw new Error(`Unary: DataType ${input.dataType} not supported`);
    }
    const newData = new DataArrayConstructor[input.dataType](input.data.length),
      { alpha } = this;
    for (let i = 0; i < newData.length; i++) {
      const sv = input.data[i];
      const dv = sv >= 0 ? sv : sv * alpha;
      newData[i] = dv;
    }
    const output = context.emptyTensor(input.dims, input.dataType, newData);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "LeakyRelu",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new LeakyRelu(),
    },
  ];
}
