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
    let func;
    switch (input.ndim) {
      case 1:
        func = this.copy1d;
        break;
        case 2:
          func = this.copy2d;
          break;
          case 3:
            func = this.copy3d;
            break;
            case 4:
              func = this.copy4d;
              break;
              case 5:
                func = this.copy5d;
                break;
                case 6:
                  func = this.copy6d;
                  break;
                default:
                  throw new Error(`Transpose: ndim ${input.ndim} > 4 is not yet supported`);
    }
    func(input.data, output.data, outShape, inStrides);
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
  
  copy5d(
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
            for (let a4 = 0; a4 < outShape[4]; a4++) {
            dO[idx++] =
              dI[
                a0 * inStrides[0] +
                  a1 * inStrides[1] +
                  a2 * inStrides[2] +
                  a3 * inStrides[3] +
                  a4 * inStrides[4]
              ];
          }}
        }
      }
    }
  }

  copy6d(
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
            for (let a4 = 0; a4 < outShape[4]; a4++) {
              for (let a5 = 0; a5 < outShape[5]; a5++) {
            dO[idx++] =
              dI[
                a0 * inStrides[0] +
                  a1 * inStrides[1] +
                  a2 * inStrides[2] +
                  a3 * inStrides[3] +
                  a4 * inStrides[4] +
                  a5 * inStrides[5]
              ];
          }}}
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
