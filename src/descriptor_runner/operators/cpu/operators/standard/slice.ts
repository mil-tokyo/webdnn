import { DataArrayTypes } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

/*
 * Opset 10
 * opset 1では区間指定がattributeなので互換性なし
 */
class Slice10 extends OperatorImpl {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const data = inputs[0],
      starts = inputs[1],
      ends = inputs[2],
      axesTensor = inputs[3];
    let steps = inputs[4];
    let axes: number[];
    if (axesTensor) {
      axes = Array.from(axesTensor.data);
      for (let i = 0; i < axes.length; i++) {
        if (axes[i] < 0) {
          axes[i] += data.ndim;
        }
      }
    } else {
      axes = [];
      for (let i = 0; i < data.ndim; i++) {
        axes.push(i);
      }
    }
    // Currently, only common usage is supported
    if (!steps) {
      steps = context.emptyTensor([axes.length], "int32");
      steps.data.fill(1);
    }
    const ranges = data.dims.map((d) => [0, d, 1, d]); // Start, stop, step, srcsize
    for (let i = 0; i < axes.length; i++) {
      ranges[axes[i]] = [
        starts.data[i],
        ends.data[i],
        steps.data[i],
        data.dims[axes[i]],
      ];
    }
    const rangesWithSize = ranges.map(([start, stop, step, srcsize]) => {
        if (start < 0) {
          start += srcsize;
        }
        start = Math.max(Math.min(start, srcsize - 1), 0);
        if (stop < 0) {
          stop += srcsize;
        }
        stop = Math.max(Math.min(stop, srcsize), -1);
        const dstsize = Math.max(Math.ceil((stop - start) / step), 0);
        return [start, stop, step, srcsize, dstsize];
      }),
      output = context.emptyTensor(
        rangesWithSize.map(([, , , , dstsize]) => dstsize),
        data.dataType
      );
    let func;
    switch (data.ndim) {
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
                throw new Error(`Slice: input dimension ${data.ndim} > 4 is not yet supported`);
    }
    func(
      data.data,
      output.data,
      rangesWithSize,
      data.strides,
      output.strides
    );
    return [output];
  }

  copy1d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    rangesWithSize: number[][],
    srcStrides: ReadonlyArray<number>,
    dstStrides: ReadonlyArray<number>
  ) {
    for (let x = 0; x < rangesWithSize[0][4]; x++) {
      dO[x * dstStrides[0]] =
        dI[(rangesWithSize[0][0] + x * rangesWithSize[0][2]) * srcStrides[0]];
    }
  }

  copy2d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    rangesWithSize: number[][],
    srcStrides: ReadonlyArray<number>,
    dstStrides: ReadonlyArray<number>
  ) {
    for (let y = 0; y < rangesWithSize[0][4]; y++) {
      for (let x = 0; x < rangesWithSize[1][4]; x++) {
        dO[y * dstStrides[0] + x * dstStrides[1]] =
          dI[
            (rangesWithSize[0][0] + y * rangesWithSize[0][2]) * srcStrides[0] +
              (rangesWithSize[1][0] + x * rangesWithSize[1][2]) * srcStrides[1]
          ];
      }
    }
  }

  copy3d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    rangesWithSize: number[][],
    srcStrides: ReadonlyArray<number>,
    dstStrides: ReadonlyArray<number>
  ) {
    for (let d0 = 0; d0 < rangesWithSize[0][4]; d0++) {
      for (let d1 = 0; d1 < rangesWithSize[1][4]; d1++) {
        for (let d2 = 0; d2 < rangesWithSize[2][4]; d2++) {
        dO[d0 * dstStrides[0] + d1 * dstStrides[1]+ d2 * dstStrides[2]] =
          dI[
            (rangesWithSize[0][0] + d0 * rangesWithSize[0][2]) * srcStrides[0] +
              (rangesWithSize[1][0] + d1 * rangesWithSize[1][2]) * srcStrides[1] +
              (rangesWithSize[2][0] + d1 * rangesWithSize[2][2]) * srcStrides[2]
          ];
      }
      }
    }
  }

  copy4d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    rangesWithSize: number[][],
    srcStrides: ReadonlyArray<number>,
    dstStrides: ReadonlyArray<number>
  ) {
    for (let d0 = 0; d0 < rangesWithSize[0][4]; d0++) {
      for (let d1 = 0; d1 < rangesWithSize[1][4]; d1++) {
        for (let d2 = 0; d2 < rangesWithSize[2][4]; d2++) {
          for (let d3 = 0; d3 < rangesWithSize[3][4]; d3++) {
        dO[d0 * dstStrides[0] + d1 * dstStrides[1]+ d2 * dstStrides[2]+ d3 * dstStrides[3]] =
          dI[
            (rangesWithSize[0][0] + d0 * rangesWithSize[0][2]) * srcStrides[0] +
              (rangesWithSize[1][0] + d1 * rangesWithSize[1][2]) * srcStrides[1] +
              (rangesWithSize[2][0] + d2 * rangesWithSize[2][2]) * srcStrides[2] +
              (rangesWithSize[3][0] + d3 * rangesWithSize[3][2]) * srcStrides[3]
          ];
        }
      }
      }
    }
  }
  
  copy5d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    rangesWithSize: number[][],
    srcStrides: ReadonlyArray<number>,
    dstStrides: ReadonlyArray<number>
  ) {
    for (let d0 = 0; d0 < rangesWithSize[0][4]; d0++) {
      for (let d1 = 0; d1 < rangesWithSize[1][4]; d1++) {
        for (let d2 = 0; d2 < rangesWithSize[2][4]; d2++) {
          for (let d3 = 0; d3 < rangesWithSize[3][4]; d3++) {
            for (let d4 = 0; d4 < rangesWithSize[4][4]; d4++) {
        dO[d0 * dstStrides[0] + d1 * dstStrides[1]+ d2 * dstStrides[2]+ d3 * dstStrides[3]+ d4 * dstStrides[4]] =
          dI[
            (rangesWithSize[0][0] + d0 * rangesWithSize[0][2]) * srcStrides[0] +
              (rangesWithSize[1][0] + d1 * rangesWithSize[1][2]) * srcStrides[1] +
              (rangesWithSize[2][0] + d2 * rangesWithSize[2][2]) * srcStrides[2] +
              (rangesWithSize[3][0] + d3 * rangesWithSize[3][2]) * srcStrides[3] +
              (rangesWithSize[4][0] + d4 * rangesWithSize[4][2]) * srcStrides[4]
          ];
        }
        }
      }
      }
    }
  }

  copy6d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    rangesWithSize: number[][],
    srcStrides: ReadonlyArray<number>,
    dstStrides: ReadonlyArray<number>
  ) {
    for (let d0 = 0; d0 < rangesWithSize[0][4]; d0++) {
      for (let d1 = 0; d1 < rangesWithSize[1][4]; d1++) {
        for (let d2 = 0; d2 < rangesWithSize[2][4]; d2++) {
          for (let d3 = 0; d3 < rangesWithSize[3][4]; d3++) {
            for (let d4 = 0; d4 < rangesWithSize[4][4]; d4++) {
              for (let d5 = 0; d5 < rangesWithSize[5][4]; d5++) {
        dO[d0 * dstStrides[0] + d1 * dstStrides[1]+ d2 * dstStrides[2]+ d3 * dstStrides[3]+ d4 * dstStrides[4]+ d5 * dstStrides[5]] =
          dI[
            (rangesWithSize[0][0] + d0 * rangesWithSize[0][2]) * srcStrides[0] +
              (rangesWithSize[1][0] + d1 * rangesWithSize[1][2]) * srcStrides[1] +
              (rangesWithSize[2][0] + d2 * rangesWithSize[2][2]) * srcStrides[2] +
              (rangesWithSize[3][0] + d3 * rangesWithSize[3][2]) * srcStrides[3] +
              (rangesWithSize[4][0] + d4 * rangesWithSize[4][2]) * srcStrides[4] +
              (rangesWithSize[5][0] + d5 * rangesWithSize[5][2]) * srcStrides[5]
          ];
        }}
        }
      }
      }
    }
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Slice",
      backend: "cpu",
      opsetMin: 10,
      factory: () => new Slice10(),
    },
  ];
}
