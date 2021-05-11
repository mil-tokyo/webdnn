import { broadcastUni } from "../../../operatorUtil";
import { Gemm } from "../../../base/gemm";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

// version 13
class CpuGemm extends Gemm {
  alpha!: number;
  beta!: number;
  transA!: number;
  transB!: number;

  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const inputA = inputs[0];
    const inputB = inputs[1];
    const inputC = inputs[2];
    const {
      m,
      n,
      k,
      strideA: [strideA0, strideA1],
      strideB: [strideB0, strideB1],
    } = this.calcShape(inputA.dims, inputB.dims);

    const newData = new Float32Array(m * n);
    const dA = inputA.data;
    const dB = inputB.data;
    const alpha = this.alpha;
    for (let i = 0; i < m; i++) {
      for (let j = 0; j < n; j++) {
        let sum = 0;
        for (let x = 0; x < k; x++) {
          sum +=
            dA[i * strideA0 + x * strideA1] * dB[x * strideB0 + j * strideB1];
        }
        sum *= alpha;
        newData[i * n + j] = sum;
      }
    }

    if (inputC) {
      const [strideC0, strideC1] = broadcastUni([m, n], inputC.dims);
      const dC = inputC.data;
      const beta = this.beta;
      for (let i = 0; i < m; i++) {
        for (let j = 0; j < n; j++) {
          newData[i * n + j] += dC[i * strideC0 + j * strideC1] * beta;
        }
      }
    }
    const output = context.emptyTensor([m, n], "float32", newData);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Gemm",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CpuGemm(),
    },
  ];
}
