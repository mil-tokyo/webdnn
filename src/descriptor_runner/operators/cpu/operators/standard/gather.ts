import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrInt } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class Gather extends OperatorImpl {
  axis!: number;

  constructor() {
    super("cpu");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axis = getAttrInt(attribute, "axis", 0);
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const data = inputs[0];
    const indices = inputs[1];
    const axis = this.axis;
    if (!(data.ndim === 1 && indices.ndim === 0 && axis === 0)) {
      throw new Error(
        "Gather: currently supports data.ndim === 1 && indices.ndim === 0 && axis === 0"
      );
    }
    const output = context.emptyTensor([], data.dataType);
    output.data[0] = data.data[indices.data[0]];
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Gather",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new Gather(),
    },
  ];
}
