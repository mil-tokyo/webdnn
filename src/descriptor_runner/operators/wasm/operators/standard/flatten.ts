import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { WebDNNWasmContext } from "../../../../interface/backend/wasm/wasmContext";
import { Flatten } from "../../../base/flatten";

class WasmFlatten extends Flatten {
  constructor() {
    super("wasm");
  }

  async run(context: WebDNNWasmContext, inputs: Tensor[]): Promise<Tensor[]> {
    // TODO: avoid copy
    const input = inputs[0];
    context.assertsWasmTensor(input);
    const computedShape = this.calcShape(input),
      output = context.emptyTensor(computedShape, input.dataType);
    context.runKernel("kernel_copy", [
      { type: "tensor", value: input },
      { type: "tensor", value: output },
      { type: "int32", value: output.length },
    ]);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Flatten",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmFlatten(),
    },
  ];
}
