import { Tensor } from "../../core/tensor";

export interface WasmSharedBufferInterface {
  backendBufferId: number;
}
export interface WasmTensor extends Tensor {
  sharedBuffer: WasmSharedBufferInterface;
}
