import { Backend } from "../../../../interface/core/constants";
import { Reshape5 } from "../../../base/reshape5";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { WebDNNWasmContext } from "../../../../interface/backend/wasm/wasmContext";

class WasmReshape5 extends Reshape5 {
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
      shapeTensor = inputs[1];
    context.assertsWasmTensor(input);
    context.cpuContext.assertsCPUTensor(shapeTensor);
    const computedShape = this.calcShape(input, shapeTensor),
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
      opType: "Reshape",
      backend: "wasm",
      opsetMin: 5,
      factory: () => new WasmReshape5(),
    },
  ];
}
