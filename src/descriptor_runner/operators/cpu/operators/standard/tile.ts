import { DataArrayTypes } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

/*
 * Opset 6
 * opset 1は互換性なし
 */
class Tile6 extends OperatorImpl {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      repeats = inputs[1];
    const outputShape: number[] = [];
    for (let i = 0; i < input.ndim; i++) {
      outputShape.push(input.dims[i] * repeats.data[i]);
    }
    const output = context.emptyTensor(outputShape, input.dataType);
    if (input.ndim === 1) {
      this.copy1d(
        input.data,
        output.data,
        input.dims,
        outputShape,
        input.strides,
        output.strides
      );
    } else if (input.ndim === 2) {
      this.copy2d(
        input.data,
        output.data,
        input.dims,
        outputShape,
        input.strides,
        output.strides
      );
    } else if (input.ndim === 3) {
      this.copy3d(
        input.data,
        output.data,
        input.dims,
        outputShape,
        input.strides,
        output.strides
      );
    } else if (input.ndim === 4) {
      this.copy4d(
        input.data,
        output.data,
        input.dims,
        outputShape,
        input.strides,
        output.strides
      );
    } else {
      throw new Error(
        `Tile: input.ndim = ${input.ndim} > 4 is not yet supported`
      );
    }
    return [output];
  }

  copy1d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      dO[d0 * outputStrides[0]] = dI[(d0 % inputShape[0]) * inputStrides[0]];
    }
  }

  copy2d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      for (let d1 = 0; d1 < outputShape[1]; d1++) {
        dO[d0 * outputStrides[0] + d1 * outputStrides[1]] =
          dI[
            (d0 % inputShape[0]) * inputStrides[0] +
              (d1 % inputShape[1]) * inputStrides[1]
          ];
      }
    }
  }

  copy3d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      for (let d1 = 0; d1 < outputShape[1]; d1++) {
        for (let d2 = 0; d2 < outputShape[2]; d2++) {
          dO[
            d0 * outputStrides[0] +
              d1 * outputStrides[1] +
              d2 * outputStrides[2]
          ] =
            dI[
              (d0 % inputShape[0]) * inputStrides[0] +
                (d1 % inputShape[1]) * inputStrides[1] +
                (d2 % inputShape[2]) * inputStrides[2]
            ];
        }
      }
    }
  }

  copy4d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      for (let d1 = 0; d1 < outputShape[1]; d1++) {
        for (let d2 = 0; d2 < outputShape[2]; d2++) {
          for (let d3 = 0; d3 < outputShape[3]; d3++) {
            dO[
              d0 * outputStrides[0] +
                d1 * outputStrides[1] +
                d2 * outputStrides[2] +
                d3 * outputStrides[3]
            ] =
              dI[
                (d0 % inputShape[0]) * inputStrides[0] +
                  (d1 % inputShape[1]) * inputStrides[1] +
                  (d2 % inputShape[2]) * inputStrides[2] +
                  (d3 % inputShape[3]) * inputStrides[3]
              ];
          }
        }
      }
    }
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Tile",
      backend: "cpu",
      opsetMin: 6,
      factory: () => new Tile6(),
    },
  ];
}
