import { DataArrayTypes } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { onnx } from "onnx-proto";
import { getAttrString } from "../../../operatorUtil";

/*
 * Opset 11
 * opset 2は互換性なし
 */
class Pad11 extends OperatorImpl {
  mode!: string;

  constructor() {
    super("cpu");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.mode = getAttrString(attribute, "mode", "constant");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      pads = Array.from(inputs[1].data),
      constantValueTensor = inputs[2];
    if (this.mode !== "constant") {
      throw new Error("Pad: mode !== constant is not yet supported");
    }
    let constantValue = 0;
    if (constantValueTensor) {
      constantValue = constantValueTensor.data[0];
    }
    const outputShape: number[] = [];
    for (let i = 0; i < input.ndim; i++) {
      outputShape.push(input.dims[i] + pads[i] + pads[i + input.ndim]);
    }
    const output = context.emptyTensor(outputShape, input.dataType);
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
        throw new Error(
          `Pad: input.ndim = ${input.ndim} > 6 is not yet supported`
        );
    }
    func(
      input.data,
      output.data,
      input.dims,
      outputShape,
      input.strides,
      output.strides,
      pads,
      constantValue
    );
    return [output];
  }

  copy1d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>,
    constantValue: number
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      const i0 = d0 - pads[0];
      let v: number;
      if (i0 < 0 || i0 >= inputShape[0]) {
        v = constantValue;
      } else {
        v = dI[i0 * inputStrides[0]];
      }
      dO[d0 * outputStrides[0]] = v;
    }
  }

  copy2d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>,
    constantValue: number
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      for (let d1 = 0; d1 < outputShape[1]; d1++) {
        const i0 = d0 - pads[0],
          i1 = d1 - pads[1];
        let v: number;
        if (i0 < 0 || i0 >= inputShape[0] || i1 < 0 || i1 >= inputShape[1]) {
          v = constantValue;
        } else {
          v = dI[i0 * inputStrides[0] + i1 * inputStrides[1]];
        }
        dO[d0 * outputStrides[0] + d1 * outputStrides[1]] = v;
      }
    }
  }
  copy3d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>,
    constantValue: number
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      for (let d1 = 0; d1 < outputShape[1]; d1++) {
        for (let d2 = 0; d2 < outputShape[2]; d2++) {
          const i0 = d0 - pads[0],
            i1 = d1 - pads[1],
            i2 = d2 - pads[2];
          let v: number;
          if (
            i0 < 0 ||
            i0 >= inputShape[0] ||
            i1 < 0 ||
            i1 >= inputShape[1] ||
            i2 < 0 ||
            i2 >= inputShape[2]
          ) {
            v = constantValue;
          } else {
            v =
              dI[
                i0 * inputStrides[0] +
                  i1 * inputStrides[1] +
                  i2 * inputStrides[2]
              ];
          }
          dO[
            d0 * outputStrides[0] +
              d1 * outputStrides[1] +
              d2 * outputStrides[2]
          ] = v;
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
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>,
    constantValue: number
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      for (let d1 = 0; d1 < outputShape[1]; d1++) {
        for (let d2 = 0; d2 < outputShape[2]; d2++) {
          for (let d3 = 0; d3 < outputShape[3]; d3++) {
            const i0 = d0 - pads[0],
              i1 = d1 - pads[1],
              i2 = d2 - pads[2],
              i3 = d3 - pads[3];
            let v: number;
            if (
              i0 < 0 ||
              i0 >= inputShape[0] ||
              i1 < 0 ||
              i1 >= inputShape[1] ||
              i2 < 0 ||
              i2 >= inputShape[2] ||
              i3 < 0 ||
              i3 >= inputShape[3]
            ) {
              v = constantValue;
            } else {
              v =
                dI[
                  i0 * inputStrides[0] +
                    i1 * inputStrides[1] +
                    i2 * inputStrides[2] +
                    i3 * inputStrides[3]
                ];
            }
            dO[
              d0 * outputStrides[0] +
                d1 * outputStrides[1] +
                d2 * outputStrides[2] +
                d3 * outputStrides[3]
            ] = v;
          }
        }
      }
    }
  }

  copy5d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>,
    constantValue: number
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      for (let d1 = 0; d1 < outputShape[1]; d1++) {
        for (let d2 = 0; d2 < outputShape[2]; d2++) {
          for (let d3 = 0; d3 < outputShape[3]; d3++) {
            for (let d4 = 0; d4 < outputShape[4]; d4++) {
              const i0 = d0 - pads[0],
                i1 = d1 - pads[1],
                i2 = d2 - pads[2],
                i3 = d3 - pads[3],
                i4 = d4 - pads[4];
              let v: number;
              if (
                i0 < 0 ||
                i0 >= inputShape[0] ||
                i1 < 0 ||
                i1 >= inputShape[1] ||
                i2 < 0 ||
                i2 >= inputShape[2] ||
                i3 < 0 ||
                i3 >= inputShape[3] ||
                i4 < 0 ||
                i4 >= inputShape[4]
              ) {
                v = constantValue;
              } else {
                v =
                  dI[
                    i0 * inputStrides[0] +
                      i1 * inputStrides[1] +
                      i2 * inputStrides[2] +
                      i3 * inputStrides[3] +
                      i4 * inputStrides[4]
                  ];
              }
              dO[
                d0 * outputStrides[0] +
                  d1 * outputStrides[1] +
                  d2 * outputStrides[2] +
                  d3 * outputStrides[3] +
                  d4 * outputStrides[4]
              ] = v;
            }
          }
        }
      }
    }
  }

  copy6d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>,
    constantValue: number
  ) {
    for (let d0 = 0; d0 < outputShape[0]; d0++) {
      for (let d1 = 0; d1 < outputShape[1]; d1++) {
        for (let d2 = 0; d2 < outputShape[2]; d2++) {
          for (let d3 = 0; d3 < outputShape[3]; d3++) {
            for (let d4 = 0; d4 < outputShape[4]; d4++) {
              for (let d5 = 0; d5 < outputShape[5]; d5++) {
                const i0 = d0 - pads[0],
                  i1 = d1 - pads[1],
                  i2 = d2 - pads[2],
                  i3 = d3 - pads[3],
                  i4 = d4 - pads[4],
                  i5 = d5 - pads[5];
                let v: number;
                if (
                  i0 < 0 ||
                  i0 >= inputShape[0] ||
                  i1 < 0 ||
                  i1 >= inputShape[1] ||
                  i2 < 0 ||
                  i2 >= inputShape[2] ||
                  i3 < 0 ||
                  i3 >= inputShape[3] ||
                  i4 < 0 ||
                  i4 >= inputShape[4] ||
                  i5 < 0 ||
                  i5 >= inputShape[5]
                ) {
                  v = constantValue;
                } else {
                  v =
                    dI[
                      i0 * inputStrides[0] +
                        i1 * inputStrides[1] +
                        i2 * inputStrides[2] +
                        i3 * inputStrides[3] +
                        i4 * inputStrides[4] +
                        i5 * inputStrides[5]
                    ];
                }
                dO[
                  d0 * outputStrides[0] +
                    d1 * outputStrides[1] +
                    d2 * outputStrides[2] +
                    d3 * outputStrides[3] +
                    d4 * outputStrides[4] +
                    d5 * outputStrides[5]
                ] = v;
              }
            }
          }
        }
      }
    }
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Pad",
      backend: "cpu",
      opsetMin: 11,
      factory: () => new Pad11(),
    },
  ];
}
