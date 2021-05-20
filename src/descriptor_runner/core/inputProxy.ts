import { DataType } from "../interface/core/constants";
import { arrayProd } from "../operators/operatorUtil";

export class InputProxy implements ArrayLike<number> {
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
    /*
     * For large length, error occurs (RangeError: Maximum call stack size exceeded)
     * Array.prototype.push.apply( this, new Array(length) );
     */
  }

  set(array: ArrayLike<number>): void {
    for (let i = 0; i < array.length; i++) {
      this[i] = array[i];
    }
  }
}
