import { Backend, DataArrayTypes, DataType } from "./constants";

export interface Tensor {
  readonly dims: ReadonlyArray<number>;
  readonly ndim: number;
  readonly length: number;
  readonly strides: ReadonlyArray<number>;
  readonly dataType: DataType;
  readonly backend: Backend;

  getData(): Promise<DataArrayTypes>;
  setData(data: DataArrayTypes): Promise<void>;
  dispose(): void;
}
