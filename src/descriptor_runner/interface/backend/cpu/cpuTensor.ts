import { DataArrayTypes } from "../../core/constants";
import { Tensor } from "../../core/tensor";

export interface CPUTensor extends Tensor {
  data: DataArrayTypes;
  getDataSync(): DataArrayTypes;
  getValue(idxs: number[]): number;
  setValue(value: number, idxs: number[]): void;
}
