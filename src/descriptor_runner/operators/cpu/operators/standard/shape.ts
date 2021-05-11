import { Backend } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class Shape extends OperatorImpl {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    // メタデータしか使わないので、どのバックエンドに存在してもよい
    const input = inputs[0];
    const shapeData = new Int32Array(input.dims);
    const output = context.emptyTensor([shapeData.length], "int32", shapeData);
    return [output];
  }

  getTensorBackendRequirement(
    nInputs: number,
    nOutputs: number
  ): (Backend | null)[] {
    // メタデータしか使わないので、どのバックエンドに存在してもよい
    return [null];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Shape",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new Shape(),
    },
  ];
}
