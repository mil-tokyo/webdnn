import { BackendContext } from "../../core/backendContext";
import { DataArrayTypes, DataType } from "../../core/constants";
import { Tensor } from "../../core/tensor";
import { CPUTensor } from "./cpuTensor";

export interface WebDNNCPUContext extends BackendContext {
  backend: "cpu";
  initialize(): Promise<void>;
  isCPUTensor(tensor: Tensor): tensor is CPUTensor;
  assertsCPUTensor(tensor: Tensor): asserts tensor is CPUTensor;
  assertsCPUTensorArray(tensors: Tensor[]): asserts tensors is CPUTensor[];
  emptyTensor(
    dims: ReadonlyArray<number>,
    dataType?: DataType,
    data?: DataArrayTypes
  ): CPUTensor;
  // eslint-disable-next-line @typescript-eslint/ban-types
  moveTensor(tensor: Tensor, option: {}): Promise<CPUTensor>;
}
