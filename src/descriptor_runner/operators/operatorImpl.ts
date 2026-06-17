import { onnx } from "onnx-proto";
import { Backend } from "../interface/core/constants";
import { TensorImpl } from "../core/tensorImpl";
import { Operator } from "../interface/core/operator";
import { BackendContext } from "../interface/core/backendContext";

export abstract class OperatorImpl implements Operator {
  constructor(public backend: Backend) {}

  abstract run(
    context: BackendContext,
    inputs: TensorImpl[],
    nOutputs: number,
  ): Promise<TensorImpl[]>;

  initialize(attribute: onnx.IAttributeProto[]): void {}

  getTensorBackendRequirement(
    nInputs: number,

    nOutputs: number,
  ): (Backend | null)[] {
    const backends: Backend[] = [];
    for (let i = 0; i < nInputs; i++) {
      backends.push(this.backend);
    }
    return backends;
  }
}
