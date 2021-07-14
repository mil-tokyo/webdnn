import { DataArrayTypes, DataType } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { broadcastMulti } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class EachElementwise extends OperatorImpl {
  constructor(
    private opType: string,
    private op: (values: number[]) => number,
    private allowDataTypes: DataType[]
  ) {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    for (const inputX of inputs) {
      if (inputX.dataType !== inputs[0].dataType) {
        throw new Error(
          `${this.opType}: input dataTypes mismatch: ${inputX.dataType} !== ${inputs[0].dataType}`
        );
      }
    }
    if (!this.allowDataTypes.includes(inputs[0].dataType)) {
      throw new Error(
        `${this.opType}: input dataType ${inputs[0].dataType} is not supported`
      );
    }
    // TODO: broadcast不要の場合に特化したパフォーマンス向上

    const { dims: outShape, allStrides: inAllStrides } = broadcastMulti(
        inputs.map((input) => input.dims)
      ),
      output = context.emptyTensor(outShape, inputs[0].dataType),
      { op } = this;
    const inputDataList = inputs.map((input) => input.data);
    switch (outShape.length) {
      case 0:
        this.op0d(inputDataList, output.data, op, outShape, inAllStrides);
        break;
      case 1:
        this.op1d(inputDataList, output.data, op, outShape, inAllStrides);
        break;
      case 2:
        this.op2d(inputDataList, output.data, op, outShape, inAllStrides);
        break;
      case 3:
        this.op3d(inputDataList, output.data, op, outShape, inAllStrides);
        break;
      case 4:
        this.op4d(inputDataList, output.data, op, outShape, inAllStrides);
        break;
      default:
        throw new Error(`Binary: input ndim > 4 is not yet supported`);
    }
    return [output];
  }

  private op0d(
    dIs: DataArrayTypes[],
    dO: DataArrayTypes,
    op: (values: number[]) => number,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    outShape: number[],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    inAllStrides: number[][]
  ) {
    dO[0] = op(dIs.map((dI) => dI[0]));
  }

  private op1d(
    dIs: DataArrayTypes[],
    dO: DataArrayTypes,
    op: (values: number[]) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      const values: number[] = [];
      for (let i = 0; i < dIs.length; i++) {
        values.push(dIs[i][a0 * inAllStrides[i][0]]);
      }
      dO[idx++] = op(values);
    }
  }

  private op2d(
    dIs: DataArrayTypes[],
    dO: DataArrayTypes,
    op: (values: number[]) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        const values: number[] = [];
        for (let i = 0; i < dIs.length; i++) {
          values.push(
            dIs[i][a0 * inAllStrides[i][0] + a1 * inAllStrides[i][1]]
          );
        }
        dO[idx++] = op(values);
      }
    }
  }

  private op3d(
    dIs: DataArrayTypes[],
    dO: DataArrayTypes,
    op: (values: number[]) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        for (let a2 = 0; a2 < outShape[2]; a2++) {
          const values: number[] = [];
          for (let i = 0; i < dIs.length; i++) {
            values.push(
              dIs[i][
                a0 * inAllStrides[i][0] +
                  a1 * inAllStrides[i][1] +
                  a2 * inAllStrides[i][2]
              ]
            );
          }
          dO[idx++] = op(values);
        }
      }
    }
  }

  private op4d(
    dIs: DataArrayTypes[],
    dO: DataArrayTypes,
    op: (values: number[]) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        for (let a2 = 0; a2 < outShape[2]; a2++) {
          for (let a3 = 0; a3 < outShape[3]; a3++) {
            const values: number[] = [];
            for (let i = 0; i < dIs.length; i++) {
              values.push(
                dIs[i][
                  a0 * inAllStrides[i][0] +
                    a1 * inAllStrides[i][1] +
                    a2 * inAllStrides[i][2] +
                    a3 * inAllStrides[i][3]
                ]
              );
            }
            dO[idx++] = op(values);
          }
        }
      }
    }
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Max",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new EachElementwise("Max", (values) => Math.max(...values), [
          "float32",
          "int32",
        ]),
    },
    {
      opType: "Mean",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new EachElementwise(
          "Mean",
          (values) => values.reduce((s, v) => s + v, 0) / values.length,
          ["float32"]
        ),
    },
    {
      opType: "Min",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new EachElementwise("Min", (values) => Math.min(...values), [
          "float32",
          "int32",
        ]),
    },
    {
      opType: "Sum",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new EachElementwise(
          "Sum",
          (values) => values.reduce((s, v) => s + v, 0),
          ["float32", "int32"]
        ),
    },
  ];
}
