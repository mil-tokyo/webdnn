namespace WebDNN {
  export class MatrixBase {
    shape: number[];
    ndim: number;
    size: number;
    dtype: string;
    backend: string;

    constructor(shape: number[]) {
      this.dtype = 'float32';
      this.shape = shape;
      this.ndim = shape.length;
      let size = 1;
      for (let i = 0; i < this.ndim; i++) {
        size *= shape[i];
      }
      this.size = size;
    }
  }
}
