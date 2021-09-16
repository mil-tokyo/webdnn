import { OperatorImpl } from "../../../operatorImpl";
import {
  WasmKernelArgument,
  WebDNNWasmContext,
} from "../../../../interface/backend/wasm/wasmContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { onnx } from "onnx-proto";
import { getAttrFloat } from "../../../operatorUtil";

abstract class WasmDynamicUnary extends OperatorImpl {
  constructor(private kernelName: string) {
    super("wasm");
  }

  protected abstract getKernelArgs(): WasmKernelArgument[];

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
      ...this.getKernelArgs(),
    ]);
    return [output];
  }
}

class WasmLeakyRelu extends WasmDynamicUnary {
  alpha!: number;

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.alpha = getAttrFloat(attribute, "alpha", 0.01);
  }

  protected getKernelArgs(): WasmKernelArgument[] {
    return [{ type: "float32", value: this.alpha }];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "LeakyRelu",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmLeakyRelu("kernel_leakyrelu"),
    },
  ];
}
