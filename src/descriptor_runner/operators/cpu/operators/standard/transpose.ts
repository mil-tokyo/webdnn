import { DataArrayTypes } from "../../../../interface/core/constants";
import { Transpose } from "../../../base/transpose";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class CPUTranspose extends Transpose {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      { outShape, inStrides } = this.calcShape(input),
      output = context.emptyTensor(outShape, input.dataType);
    if (input.ndim === 1) {
      this.copy1d(input.data, output.data, outShape, inStrides);
    } else if (input.ndim === 2) {
      this.copy2d(input.data, output.data, outShape, inStrides);
    } else if (input.ndim === 3) {
      this.copy3d(input.data, output.data, outShape, inStrides);
    } else if (input.ndim === 4) {
      this.copy4d(input.data, output.data, outShape, inStrides);
    } else {
      throw new Error(`Transpose: ${input.ndim} > 4 is not yet supported`);
    }
    return [output];
  }

  copy1d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    outShape: number[],
    inStrides: number[]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      dO[idx++] = dI[a0 * inStrides[0]];
    }
  }

  copy2d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    outShape: number[],
    inStrides: number[]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        dO[idx++] = dI[a0 * inStrides[0] + a1 * inStrides[1]];
      }
    }
  }

  copy3d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    outShape: number[],
    inStrides: number[]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        for (let a2 = 0; a2 < outShape[2]; a2++) {
          dO[idx++] =
            dI[a0 * inStrides[0] + a1 * inStrides[1] + a2 * inStrides[2]];
        }
      }
    }
  }

  copy4d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    outShape: number[],
    inStrides: number[]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        for (let a2 = 0; a2 < outShape[2]; a2++) {
          for (let a3 = 0; a3 < outShape[3]; a3++) {
            dO[idx++] =
              dI[
                a0 * inStrides[0] +
                  a1 * inStrides[1] +
                  a2 * inStrides[2] +
                  a3 * inStrides[3]
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
      opType: "Transpose",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUTranspose(),
    },
  ];
}
