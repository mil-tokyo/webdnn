import { onnx } from "onnx-proto";
import { BackendContext } from "./backendContext";
import { Backend } from "./constants";
import { Tensor } from "./tensor";

export interface Operator {
  backend: Backend;
  run(
    context: BackendContext,
    inputs: Tensor[],
    nOutputs: number
  ): Promise<Tensor[]>;
  initialize(attribute: onnx.IAttributeProto[]): void;
  getTensorBackendRequirement(
    nInputs: number,
    nOutputs: number
  ): (Backend | null)[];
}

export interface OperatorEntry {
  opType: string;
  // Inclusive
  opsetMin: number;
  // Exclusive, undefined means infinite
  opsetMax?: number;
  // Operator set domain. Not yet supported.
  domain?: string;
  backend: Backend;
  factory: () => Operator;
}
