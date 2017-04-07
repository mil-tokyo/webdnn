namespace WebDNN {
  export class MatrixCPU extends MatrixBase {
    data: Float32Array;

    constructor(shape: number[], data?: Float32Array, nocopy?: boolean) {
      super(shape);
      this.backend = 'cpu';
      if (nocopy) {
        this.data = data;
      } else if (data != null) {
        this.data = data.slice();
      } else {
        this.data = new Float32Array(this.size);
      }
    }
  }
}
