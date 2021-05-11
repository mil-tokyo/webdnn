import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { MatMul } from "../../../base/matmul";

class CpuMatMul extends MatMul {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const inputA = inputs[0];
    const inputB = inputs[1];
    if (inputA.dataType !== "float32" || inputB.dataType !== "float32") {
      throw new Error("only float32 is supported");
    }
    const {
      resultLength,
      resultDims,
      resultStrides,
      resultDimsAfterSqueeze,
      stridesA,
      stridesB,
      innerProductLength,
    } = this.calcShape(inputA.dims, inputB.dims);
    const newData = new Float32Array(resultLength);
    if (resultDims.length === 2) {
      this.calcDim2(
        inputA.data as Float32Array,
        inputB.data as Float32Array,
        newData,
        resultDims,
        resultStrides,
        stridesA,
        stridesB,
        innerProductLength
      );
    } else if (resultDims.length === 3) {
      this.calcDim3(
        inputA.data as Float32Array,
        inputB.data as Float32Array,
        newData,
        resultDims,
        resultStrides,
        stridesA,
        stridesB,
        innerProductLength
      );
    } else {
      // TODO: 4次元以上のサポート
      throw new Error();
    }

    const output = context.emptyTensor(
      resultDimsAfterSqueeze,
      "float32",
      newData
    );
    return [output];
  }

  private calcDim2(
    dA: Float32Array,
    dB: Float32Array,
    dC: Float32Array,
    resultDims: number[],
    resultStrides: number[],
    stridesA: ReadonlyArray<number>,
    stridesB: ReadonlyArray<number>,
    innerProductLength: number
  ) {
    for (let m = 0; m < resultDims[0]; m++) {
      for (let n = 0; n < resultDims[1]; n++) {
        let sum = 0;
        for (let k = 0; k < innerProductLength; k++) {
          sum +=
            dA[m * stridesA[0] + k * stridesA[1]] *
            dB[k * stridesB[0] + n * stridesB[1]];
        }
        dC[m * resultStrides[0] + n * resultStrides[1]] = sum;
      }
    }
  }

  private calcDim3(
    dA: Float32Array,
    dB: Float32Array,
    dC: Float32Array,
    resultDims: number[],
    resultStrides: number[],
    stridesA: ReadonlyArray<number>,
    stridesB: ReadonlyArray<number>,
    innerProductLength: number
  ) {
    for (let o0 = 0; o0 < resultDims[0]; o0++) {
      for (let m = 0; m < resultDims[1]; m++) {
        for (let n = 0; n < resultDims[2]; n++) {
          let sum = 0;
          for (let k = 0; k < innerProductLength; k++) {
            sum +=
              dA[o0 * stridesA[0] + m * stridesA[1] + k * stridesA[2]] *
              dB[o0 * stridesB[0] + k * stridesB[1] + n * stridesB[2]];
          }
          dC[
            o0 * resultStrides[0] + m * resultStrides[1] + n * resultStrides[2]
          ] = sum;
        }
      }
    }
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "MatMul",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CpuMatMul(),
    },
  ];
}
