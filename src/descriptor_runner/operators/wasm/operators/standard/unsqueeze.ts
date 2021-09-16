import { Backend } from "../../../../interface/core/constants";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { WebDNNWasmContext } from "../../../../interface/backend/wasm/wasmContext";
import { Unsqueeze1, Unsqueeze13 } from "../../../base/unsqueeze";

class WasmUnsqueeze1 extends Unsqueeze1 {
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

class WasmUnsqueeze13 extends Unsqueeze13 {
  constructor() {
    super("wasm");
  }

  getTensorBackendRequirement(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    nInputs: number,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    nOutputs: number
  ): (Backend | null)[] {
    return ["wasm", "cpu"];
  }

  async run(context: WebDNNWasmContext, inputs: Tensor[]): Promise<Tensor[]> {
    // TODO: avoid copy
    const input = inputs[0],
      axes = inputs[1];
    context.assertsWasmTensor(input);
    context.cpuContext.assertsCPUTensor(axes);
    const computedShape = this.calcShape(input, axes),
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
      opType: "Unsqueeze",
      backend: "wasm",
      opsetMin: 13,
      factory: () => new WasmUnsqueeze13(),
    },
    {
      opType: "Unsqueeze",
      backend: "wasm",
      opsetMin: 1,
      opsetMax: 13,
      factory: () => new WasmUnsqueeze1(),
    },
  ];
}
