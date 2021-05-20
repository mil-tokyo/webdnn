import { onnx } from "onnx-proto";
import { DataArrayTypes, DataType } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrTensor } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class Constant extends OperatorImpl {
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
      // Sparse_value, value_float etc in opset 12 is not yet supported
      throw new Error("value not exist in Constant");
    }
    this.constant = constant;
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    const output = context.emptyTensor(
      this.constant.dims,
      this.constant.dataType
    );
    output.data.set(this.constant.data);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Constant",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new Constant(),
    },
  ];
}
