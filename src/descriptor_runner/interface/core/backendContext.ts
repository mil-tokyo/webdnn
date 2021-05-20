import { Backend, DataType } from "./constants";
import { Tensor } from "./tensor";

export interface BackendContext {
  backend: Backend;
  emptyTensor(dims: ReadonlyArray<number>, dataType?: DataType): Tensor;
  moveTensor(tensor: Tensor, option: Record<string, any>): Promise<Tensor>;
}
