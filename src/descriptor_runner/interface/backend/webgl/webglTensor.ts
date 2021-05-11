import { Tensor } from "../../core/tensor";

export interface WebGLTensor extends Tensor {
  readonly textureWidth: number;
  readonly textureHeight: number;
  readonly dimPerPixel: 1 | 4;

  alias(dims: ReadonlyArray<number>): WebGLTensor;
}
