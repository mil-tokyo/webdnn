import { DataArrayTypes, DataType } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { broadcastMulti } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class Binary7 extends OperatorImpl {
  constructor(
    private op: (lhs: number, rhs: number) => number,
    private allowDataTypes: DataType[]
  ) {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const inputA = inputs[0],
      inputB = inputs[1];
    if (inputA.dataType !== inputB.dataType) {
      throw new Error(
        `Binary: input dataTypes mismatch: ${inputA.dataType} !== ${inputB.dataType}`
      );
    }
    if (!this.allowDataTypes.includes(inputA.dataType)) {
      throw new Error(
        `Binary: input dataType ${inputA.dataType} is not supported`
      );
    }
    // TODO: broadcast不要の場合に特化したパフォーマンス向上

    const { dims: outShape, allStrides: inAllStrides } = broadcastMulti([
        inputA.dims,
        inputB.dims,
      ]),
      output = context.emptyTensor(outShape, inputA.dataType),
      { op } = this;
    let func;
    switch (outShape.length) {
      case 0:
        func = this.op0d;
        break;
        case 1:
          func = this.op1d;
          break;
          case 2:
            func = this.op2d;
            break;
            case 3:
              func = this.op3d;
              break;
              case 4:
                func = this.op4d;
                break;
                case 5:
                  func = this.op5d;
                  break;
                  case 6:
                    func = this.op6d;
                    break;
      default:
        throw new Error(`Binary: input ndim ${outShape.length} > 4 is not yet supported`);
    }
    func(
      inputA.data,
      inputB.data,
      output.data,
      op,
      outShape,
      inAllStrides
    );
    return [output];
  }

  private op0d(
    dL: DataArrayTypes,
    dR: DataArrayTypes,
    dO: DataArrayTypes,
    op: (lhs: number, rhs: number) => number,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    outShape: number[],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    inAllStrides: number[][]
  ) {
    dO[0] = op(dL[0], dR[0]);
  }

  private op1d(
    dL: DataArrayTypes,
    dR: DataArrayTypes,
    dO: DataArrayTypes,
    op: (lhs: number, rhs: number) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      dO[idx++] = op(dL[a0 * inAllStrides[0][0]], dR[a0 * inAllStrides[1][0]]);
    }
  }

  private op2d(
    dL: DataArrayTypes,
    dR: DataArrayTypes,
    dO: DataArrayTypes,
    op: (lhs: number, rhs: number) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        dO[idx++] = op(
          dL[a0 * inAllStrides[0][0] + a1 * inAllStrides[0][1]],
          dR[a0 * inAllStrides[1][0] + a1 * inAllStrides[1][1]]
        );
      }
    }
  }

  private op3d(
    dL: DataArrayTypes,
    dR: DataArrayTypes,
    dO: DataArrayTypes,
    op: (lhs: number, rhs: number) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        for (let a2 = 0; a2 < outShape[2]; a2++) {
          dO[idx++] = op(
            dL[
              a0 * inAllStrides[0][0] +
                a1 * inAllStrides[0][1] +
                a2 * inAllStrides[0][2]
            ],
            dR[
              a0 * inAllStrides[1][0] +
                a1 * inAllStrides[1][1] +
                a2 * inAllStrides[1][2]
            ]
          );
        }
      }
    }
  }

  private op4d(
    dL: DataArrayTypes,
    dR: DataArrayTypes,
    dO: DataArrayTypes,
    op: (lhs: number, rhs: number) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        for (let a2 = 0; a2 < outShape[2]; a2++) {
          for (let a3 = 0; a3 < outShape[3]; a3++) {
            dO[idx++] = op(
              dL[
                a0 * inAllStrides[0][0] +
                  a1 * inAllStrides[0][1] +
                  a2 * inAllStrides[0][2] +
                  a3 * inAllStrides[0][3]
              ],
              dR[
                a0 * inAllStrides[1][0] +
                  a1 * inAllStrides[1][1] +
                  a2 * inAllStrides[1][2] +
                  a3 * inAllStrides[1][3]
              ]
            );
          }
        }
      }
    }
  }

  private op5d(
    dL: DataArrayTypes,
    dR: DataArrayTypes,
    dO: DataArrayTypes,
    op: (lhs: number, rhs: number) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        for (let a2 = 0; a2 < outShape[2]; a2++) {
          for (let a3 = 0; a3 < outShape[3]; a3++) {
            for (let a4 = 0; a4 < outShape[4]; a4++) {
            dO[idx++] = op(
              dL[
                a0 * inAllStrides[0][0] +
                  a1 * inAllStrides[0][1] +
                  a2 * inAllStrides[0][2] +
                  a3 * inAllStrides[0][3] +
                  a4 * inAllStrides[0][4]
              ],
              dR[
                a0 * inAllStrides[1][0] +
                  a1 * inAllStrides[1][1] +
                  a2 * inAllStrides[1][2] +
                  a3 * inAllStrides[1][3] +
                  a4 * inAllStrides[1][4]
              ]
            );
            }
        }
      }
    }
  }
}

  private op6d(
    dL: DataArrayTypes,
    dR: DataArrayTypes,
    dO: DataArrayTypes,
    op: (lhs: number, rhs: number) => number,
    outShape: number[],
    inAllStrides: number[][]
  ) {
    let idx = 0;
    for (let a0 = 0; a0 < outShape[0]; a0++) {
      for (let a1 = 0; a1 < outShape[1]; a1++) {
        for (let a2 = 0; a2 < outShape[2]; a2++) {
          for (let a3 = 0; a3 < outShape[3]; a3++) {
            for (let a4 = 0; a4 < outShape[4]; a4++) {
              for (let a5 = 0; a5 < outShape[5]; a5++) {
            dO[idx++] = op(
              dL[
                a0 * inAllStrides[0][0] +
                  a1 * inAllStrides[0][1] +
                  a2 * inAllStrides[0][2] +
                  a3 * inAllStrides[0][3] +
                  a4 * inAllStrides[0][4] +
                  a5 * inAllStrides[0][5]
              ],
              dR[
                a0 * inAllStrides[1][0] +
                  a1 * inAllStrides[1][1] +
                  a2 * inAllStrides[1][2] +
                  a3 * inAllStrides[1][3] +
                  a4 * inAllStrides[1][4] +
                  a5 * inAllStrides[1][5]
              ]
            );
              }}
          }
        }
      }
    }
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    // Add, Sub, Mul, Div, Pow: opset under 7 requires explicit broadcast flag
    {
      opType: "Add",
      backend: "cpu",
      opsetMin: 7,
      factory: () => new Binary7((lhs, rhs) => lhs + rhs, ["float32", "int32"]),
    },
    {
      opType: "Sub",
      backend: "cpu",
      opsetMin: 7,
      factory: () => new Binary7((lhs, rhs) => lhs - rhs, ["float32", "int32"]),
    },
    {
      opType: "Mul",
      backend: "cpu",
      opsetMin: 7,
      factory: () => new Binary7((lhs, rhs) => lhs * rhs, ["float32", "int32"]),
    },
    {
      opType: "Div",
      backend: "cpu",
      opsetMin: 7,
      factory: () => new Binary7((lhs, rhs) => lhs / rhs, ["float32", "int32"]),
    },
    {
      opType: "Pow",
      backend: "cpu",
      opsetMin: 7,
      factory: () =>
        new Binary7((lhs, rhs) => lhs ** rhs, ["float32", "int32"]),
    },
  ];
}
