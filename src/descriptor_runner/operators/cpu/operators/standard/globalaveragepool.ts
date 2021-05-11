import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { averagepool } from "../../rawcomputation/averagepool";
import { OperatorEntry } from "../../../../interface/core/operator";

export class CpuGlobalAveragePool extends OperatorImpl {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const inputX = inputs[0];
    // TODO: 2D以外対応
    if (inputX.ndim !== 4) {
      throw new Error("MaxPool other than 2D is not yet supported");
    }
    const batch = inputX.dims[0];
    const ch = inputX.dims[1];
    const inShape = [inputX.dims[2], inputX.dims[3]];
    const outputData = new Float32Array(batch * ch);
    averagepool(
      inputX.data as Float32Array,
      outputData,
      true, //わずかに計算量が減る
      batch,
      inShape,
      [0, 0, 0, 0],
      [1, 1],
      inShape,
      [1, 1],
      ch
    );
    const output = context.emptyTensor(
      [batch, ch, 1, 1],
      "float32",
      outputData
    );
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "GlobalAveragePool",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CpuGlobalAveragePool(),
    },
  ];
}
