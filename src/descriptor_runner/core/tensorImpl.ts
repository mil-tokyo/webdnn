import { Backend, DataArrayTypes, DataType } from "../interface/core/constants";
import { Tensor } from "../interface/core/tensor";

export abstract class TensorImpl implements Tensor {
  readonly dims: ReadonlyArray<number>;
  readonly ndim: number;
  readonly length: number;
  readonly strides: ReadonlyArray<number>;

  constructor(
    dims: ReadonlyArray<number>,
    readonly dataType: DataType,
    readonly backend: Backend
  ) {
    this.dims = dims.slice(); //呼び出し元で誤って書き換えることを防止
    this.ndim = dims.length;
    let length = 1;
    const strides: number[] = [];
    for (let d = dims.length - 1; d >= 0; d--) {
      const dim = dims[d];
      strides.unshift(length);
      length *= dim;
    }
    this.length = length;
    this.strides = strides;
  }

  abstract getData(): Promise<DataArrayTypes>;
  abstract setData(data: DataArrayTypes): Promise<void>;
  abstract dispose(): void;
}
