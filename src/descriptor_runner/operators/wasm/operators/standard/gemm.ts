import { WebDNNWasmContext } from "../../../../interface/backend/wasm/wasmContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Gemm } from "../../../base/gemm";

class WasmGemm extends Gemm {
  constructor() {
    super("wasm");
  }

  async run(context: WebDNNWasmContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWasmTensorArray(inputs);
    const [inputA, inputB, inputC] = inputs;
    const { m, n, k } = this.calcShape(inputA.dims, inputB.dims);
    const output = context.emptyTensor([m, n]);
    if (this.alpha !== 1.0) {
      throw new Error("Gemm: alpha !== 1.0 is not yet supported");
    }
    if (inputC) {
      if (this.beta !== 1.0) {
        throw new Error("Gemm: beta !== 1.0 is not yet supported");
      }
      context.runKernel(
        `kernel_gemm_transa${this.transA ? "1" : "0"}_transb${
          this.transB ? "1" : "0"
        }_c`,
        [
          { type: "tensor", value: inputA },
          { type: "tensor", value: inputB },
          { type: "tensor", value: inputC },
          { type: "tensor", value: output },
          { type: "int32", value: m },
          { type: "int32", value: n },
          { type: "int32", value: k },
        ]
      );
    } else {
      context.runKernel(
        `kernel_gemm_transa${this.transA ? "1" : "0"}_transb${
          this.transB ? "1" : "0"
        }`,
        [
          { type: "tensor", value: inputA },
          { type: "tensor", value: inputB },
          { type: "tensor", value: output },
          { type: "int32", value: m },
          { type: "int32", value: n },
          { type: "int32", value: k },
        ]
      );
    }
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Gemm",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmGemm(),
    },
  ];
}
