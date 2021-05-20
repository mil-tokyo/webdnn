import { Unsqueeze } from "../../../base/unsqueeze";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

/*
 * Opset 1
 * opset 11以降はaxesがinputとして与えられるため非互換(また、負の軸も許容)
 */
export class CPUUnsqueeze extends Unsqueeze {
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

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Unsqueeze",
      backend: "cpu",
      opsetMin: 1,
      opsetMax: 11,
      factory: () => new CPUUnsqueeze(),
    },
  ];
}
