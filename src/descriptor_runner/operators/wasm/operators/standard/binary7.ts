import { OperatorImpl } from "../../../operatorImpl";
import {
  WasmKernelArgument,
  WasmKernelArgumentInt32,
  WebDNNWasmContext,
} from "../../../../interface/backend/wasm/wasmContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { broadcastMulti } from "../../../operatorUtil";

class WasmBinary7 extends OperatorImpl {
  constructor(private kernelName: string) {
    super("wasm");
  }

  async run(context: WebDNNWasmContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWasmTensorArray(inputs);
    const inputA = inputs[0],
      inputB = inputs[1];
    if (inputA.dataType !== "float32" || inputB.dataType !== "float32") {
      throw new Error("Only float32 is supported");
    }

    const { dims: outShape, allStrides: inAllStrides } = broadcastMulti([
      inputA.dims,
      inputB.dims,
    ]);
    const output = context.emptyTensor(outShape, inputA.dataType);
    const args: WasmKernelArgument[] = [
      { type: "tensor", value: inputA },
      { type: "tensor", value: inputB },
      { type: "tensor", value: output },
      ...outShape.map(
        (v) => ({ type: "int32", value: v } as WasmKernelArgumentInt32)
      ),
      ...inAllStrides[0].map(
        (v) => ({ type: "int32", value: v } as WasmKernelArgumentInt32)
      ),
      ...inAllStrides[1].map(
        (v) => ({ type: "int32", value: v } as WasmKernelArgumentInt32)
      ),
    ];
    context.runKernel(`kernel_${this.kernelName}_d${outShape.length}`, args);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Add",
      backend: "wasm",
      opsetMin: 7,
      factory: () => new WasmBinary7("add"),
    },
    {
      opType: "Sub",
      backend: "wasm",
      opsetMin: 7,
      factory: () => new WasmBinary7("sub"),
    },
    {
      opType: "Mul",
      backend: "wasm",
      opsetMin: 7,
      factory: () => new WasmBinary7("mul"),
    },
    {
      opType: "Div",
      backend: "wasm",
      opsetMin: 7,
      factory: () => new WasmBinary7("div"),
    },
    {
      opType: "Pow",
      backend: "wasm",
      opsetMin: 7,
      factory: () => new WasmBinary7("pow"),
    },
  ];
}
