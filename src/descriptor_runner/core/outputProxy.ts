import {
  DataArrayConstructor,
  DataArrayTypes,
  DataType,
} from "../interface/core/constants";
import { arrayProd } from "../operators/operatorUtil";

export class OutputProxy implements ArrayLike<number> {
  readonly length: number;
  [n: number]: number;
  readonly dims: ReadonlyArray<number>;

  constructor(dims: ReadonlyArray<number>, public readonly dataType: DataType) {
    this.dims = dims;
    const length = arrayProd(dims);
    this.length = length;
    for (let i = 0; i < length; i++) {
      this[i] = 0;
    }
  }

  set(array: ArrayLike<number>): void {
    for (let i = 0; i < array.length; i++) {
      this[i] = array[i];
    }
  }

  toActual(): DataArrayTypes {
    const ta = new DataArrayConstructor[this.dataType](this.length);
    for (let i = 0; i < this.length; i++) {
      ta[i] = this[i];
    }
    return ta;
  }
}
