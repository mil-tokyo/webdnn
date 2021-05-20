import { averagepool } from "../../rawcomputation/averagepool";
import { AveragePool } from "../../../base/averagepool";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

// Version 1, 7, 10, 11+
class CpuAveragePool extends AveragePool {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const inputX = inputs[0];
    // TODO: 2D以外対応
    if (inputX.ndim !== 4) {
      throw new Error("AveragePool other than 2D is not yet supported");
    }
    const { batch, kernelShape, pads, strides, inShape, outShape, ch } =
        this.calcShape(inputX.dims),
      outputData = new Float32Array(batch * outShape[0] * outShape[1] * ch);
    averagepool(
      inputX.data as Float32Array,
      outputData,
      this.countIncludePad,
      batch,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      ch
    );
    const output = context.emptyTensor(
      [batch, ch, outShape[0], outShape[1]],
      "float32",
      outputData
    );
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "AveragePool",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CpuAveragePool(),
    },
  ];
}
