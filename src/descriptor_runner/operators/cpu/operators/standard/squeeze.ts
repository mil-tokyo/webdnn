import { Unsqueeze1, Unsqueeze13 } from "../../../base/unsqueeze";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Squeeze1, Squeeze13 } from "../../../base/squeeze";

export class CPUSqueeze1 extends Squeeze1 {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      newShape = this.calcShape(input),
      output = context.emptyTensor(newShape, input.dataType, input.data);
    return [output];
  }
}

export class CPUSqueeze13 extends Squeeze13 {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      axes = inputs[1],
      newShape = this.calcShape(input, axes),
      output = context.emptyTensor(newShape, input.dataType, input.data);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Squeeze",
      backend: "cpu",
      opsetMin: 13,
      factory: () => new CPUSqueeze13(),
    },
    {
      opType: "Squeeze",
      backend: "cpu",
      opsetMin: 1,
      opsetMax: 13,
      factory: () => new CPUSqueeze1(),
    },
  ];
}
