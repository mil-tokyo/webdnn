import { Flatten } from "../../../base/flatten";
import { Tensor } from "../../../../interface/core/tensor";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { OperatorEntry } from "../../../../interface/core/operator";

class CPUFlatten extends Flatten {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      output = context.emptyTensor(
        this.calcShape(input),
        input.dataType,
        input.data
      );
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Flatten",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUFlatten(),
    },
  ];
}
