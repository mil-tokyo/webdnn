import { onnx } from "onnx-proto";
import { DataArrayTypes, DataType } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrTensor } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class ConstantOfShape extends OperatorImpl {
  constant!: {
    data: DataArrayTypes;
    dataType: DataType;
    dims: number[];
  };

  constructor() {
    super("cpu");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    const constant = getAttrTensor(attribute, "value");
    if (!constant) {
      throw new Error("value not exist in ConstantOfShape");
    }
    this.constant = constant;
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = Array.from(inputs[0].data);
    const output = context.emptyTensor(input, this.constant.dataType);
    output.data.fill(this.constant.data[0]);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "ConstantOfShape",
      backend: "cpu",
      opsetMin: 9,
      factory: () => new ConstantOfShape(),
    },
  ];
}
