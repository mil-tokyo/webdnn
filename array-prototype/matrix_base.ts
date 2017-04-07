namespace WebDNN {
  export class MatrixBase {
    shape: number[];
    strides: number[];
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
      let stride = 1;
      let strides = [];//[cols, 1]
      for (let i = this.ndim - 1; i >= 0; i--) {
        strides.unshift(stride);
        stride *= shape[i];
      }
      this.strides = strides;
      this.size = size;
    }
  }
}
