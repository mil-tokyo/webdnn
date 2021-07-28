import { CPUTensor } from "../../../..";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Split13, Split2 } from "../../../base/split";

class CPUSplit2 extends Split2 {
  constructor() {
    super("cpu");
  }

  async run(
    context: WebDNNCPUContext,
    inputs: Tensor[],
    nOutputs: number
  ): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      {
        eachOutputParams,
        outerLength,
        innerLength,
        inOuterStride,
        inConcatStride,
      } = this.calcShape(input, nOutputs),
      outputs: CPUTensor[] = [];
    for (let i = 0; i < nOutputs; i++) {
      const { dim, offset, outShape, outerStride, splitStride } =
          eachOutputParams[i],
        ot = context.emptyTensor(outShape, input.dataType);
      for (let c = 0; c < dim; c++) {
        for (let outer = 0; outer < outerLength; outer++) {
          for (let inner = 0; inner < innerLength; inner++) {
            ot.data[c * splitStride + outer * outerStride + inner] =
              input.data[
                (c + offset) * inConcatStride + outer * inOuterStride + inner
              ];
          }
        }
      }
      outputs.push(ot);
    }
    return outputs;
  }
}

class CPUSplit13 extends Split13 {
  constructor() {
    super("cpu");
  }

  async run(
    context: WebDNNCPUContext,
    inputs: Tensor[],
    nOutputs: number
  ): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      splitTensor = inputs[1],
      {
        eachOutputParams,
        outerLength,
        innerLength,
        inOuterStride,
        inConcatStride,
      } = this.calcShape(input, nOutputs, splitTensor),
      outputs: CPUTensor[] = [];
    for (let i = 0; i < nOutputs; i++) {
      const { dim, offset, outShape, outerStride, splitStride } =
          eachOutputParams[i],
        ot = context.emptyTensor(outShape, input.dataType);
      for (let c = 0; c < dim; c++) {
        for (let outer = 0; outer < outerLength; outer++) {
          for (let inner = 0; inner < innerLength; inner++) {
            ot.data[c * splitStride + outer * outerStride + inner] =
              input.data[
                (c + offset) * inConcatStride + outer * inOuterStride + inner
              ];
          }
        }
      }
      outputs.push(ot);
    }
    return outputs;
  }
}
export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Split",
      backend: "cpu",
      opsetMin: 13,
      factory: () => new CPUSplit13(),
    },
    {
      opType: "Split",
      backend: "cpu",
      opsetMin: 1,
      opsetMax: 13,
      factory: () => new CPUSplit2(),
    },
  ];
}
