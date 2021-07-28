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
    if (data.ndim === 1) {
      this.copy1d(
        data.data,
        output.data,
        rangesWithSize,
        data.strides,
        output.strides
      );
    } else if (data.ndim === 2) {
      this.copy2d(
        data.data,
        output.data,
        rangesWithSize,
        data.strides,
        output.strides
      );
    } else {
      throw new Error(`Slice: ${data.ndim} > 2 is not yet supported`);
    }
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
