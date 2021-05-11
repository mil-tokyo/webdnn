import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNWasmContext } from "../../../../interface/backend/wasm/wasmContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class WasmUnary extends OperatorImpl {
  constructor(private kernelName: string) {
    super("wasm");
  }

  async run(context: WebDNNWasmContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWasmTensorArray(inputs);
    const input = inputs[0];
    if (input.dataType !== "float32") {
      throw new Error("Only float32 is supported");
    }
    const output = context.emptyTensor(input.dims, input.dataType);
    context.runKernel(this.kernelName, [
      { type: "tensor", value: input },
      { type: "tensor", value: output },
      { type: "int32", value: input.length },
    ]);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Ceil",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmUnary("kernel_ceil"),
    },
    {
      opType: "Exp",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmUnary("kernel_exp"),
    },
    {
      opType: "Floor",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmUnary("kernel_floor"),
    },
    {
      opType: "Relu",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmUnary("kernel_relu"),
    },
    {
      opType: "Sigmoid",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmUnary("kernel_sigmoid"),
    },
    {
      opType: "Sqrt",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmUnary("kernel_sqrt"),
    },
    {
      opType: "Tanh",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmUnary("kernel_tanh"),
    },
  ];
}
