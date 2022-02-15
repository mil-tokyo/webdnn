import { DataArrayTypes } from "../../../../interface/core/constants";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { onnx } from "onnx-proto";
import { getAttrString } from "../../../operatorUtil";
import { Pad11 } from "../../../base/pad11";

/*
 * Opset 11
 * opset 2は互換性なし
 */
class CPUPad11 extends Pad11 {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const [input, shapeTensor, constantValueTensor] = inputs;
    const { outputShape, pads } = this.calcShape(input, shapeTensor);
    let constantValue = 0;
    if (constantValueTensor) {
      constantValue = constantValueTensor.data[0];
    }

    // edge:
    // [0,1,2,3] -> pad (3,3) -> [0,0,0,*0,1,2,3*,3,3,3]
    // [0,1,2,3] -> pad (6,6) -> [0,0,0,0,0,0,*0,1,2,3*,3,3,3,3,3,3]
    // reflect:
    // [0,1,2,3] -> pad (3,3) -> [3,2,1,*0,1,2,3*,2,1,0]
    // [0,1,2,3] -> pad (6,6) -> [0,1,2,3,2,1,*0,1,2,3*,2,1,0,1,2,3]
    // [0,1,2,3] -> pad (8,8) -> [2,1,0,1,2,3,2,1,*0,1,2,3*,2,1,0,1,2,3,2,1]
    const output = context.emptyTensor(outputShape, input.dataType);
    let func;
    switch (this.mode) {
      case "constant":
        switch (input.ndim) {
          case 1:
            func = this.constCopy1d;
            break;
          case 2:
            func = this.constCopy2d;
            break;
          case 3:
            func = this.constCopy3d;
            break;
          case 4:
            func = this.constCopy4d;
            break;
          case 5:
            func = this.constCopy5d;
            break;
          case 6:
            func = this.constCopy6d;
            break;
          default:
            throw new Error(
              `Pad: input.ndim = ${input.ndim} > 6 is not yet supported`
            );
        }
        break;
      case "reflect":
        switch (input.ndim) {
          case 1:
            func = this.reflectCopy1d;
            break;
          case 2:
            func = this.reflectCopy2d;
            break;
          case 3:
            func = this.reflectCopy3d;
            break;
          case 4:
            func = this.reflectCopy4d;
            break;
          case 5:
            func = this.reflectCopy5d;
            break;
          case 6:
            func = this.reflectCopy6d;
            break;
          default:
            throw new Error(
              `Pad: input.ndim = ${input.ndim} > 6 is not yet supported`
            );
        }
        break;
      case "edge":
        switch (input.ndim) {
          case 1:
            func = this.edgeCopy1d;
            break;
          case 2:
            func = this.edgeCopy2d;
            break;
          case 3:
            func = this.edgeCopy3d;
            break;
          case 4:
            func = this.edgeCopy4d;
            break;
          case 5:
            func = this.edgeCopy5d;
            break;
          case 6:
            func = this.edgeCopy6d;
            break;
          default:
            throw new Error(
              `Pad: input.ndim = ${input.ndim} > 6 is not yet supported`
            );
        }
        break;
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

  constCopy1d(
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

  constCopy2d(
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

  constCopy3d(
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

  constCopy4d(
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

  constCopy5d(
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

  constCopy6d(
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

  reflectCopy1d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0] = inputShape;
    const [outputShape0] = outputShape;
    const [inputStrides0] = inputStrides;
    const [outputStrides0] = outputStrides;
    const [pads0] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      let i0 = d0 - pads0;
      if (i0 < 0) {
        i0 = -i0 % (inputShape0 * 2 - 2);
        if (i0 >= inputShape0) {
          i0 = inputShape0 * 2 - i0 - 2;
        }
      } else if (i0 >= inputShape0) {
        i0 = i0 % (inputShape0 * 2 - 2);
        if (i0 >= inputShape0) {
          i0 = inputShape0 * 2 - i0 - 2;
        }
      }
      const v = dI[i0 * inputStrides0];
      dO[d0 * outputStrides0] = v;
    }
  }

  reflectCopy2d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0, inputShape1] = inputShape;
    const [outputShape0, outputShape1] = outputShape;
    const [inputStrides0, inputStrides1] = inputStrides;
    const [outputStrides0, outputStrides1] = outputStrides;
    const [pads0, pads1] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        let i0 = d0 - pads0,
          i1 = d1 - pads1;
        if (i0 < 0) {
          i0 = -i0 % (inputShape0 * 2 - 2);
          if (i0 >= inputShape0) {
            i0 = inputShape0 * 2 - i0 - 2;
          }
        } else if (i0 >= inputShape0) {
          i0 = i0 % (inputShape0 * 2 - 2);
          if (i0 >= inputShape0) {
            i0 = inputShape0 * 2 - i0 - 2;
          }
        }
        if (i1 < 0) {
          i1 = -i1 % (inputShape1 * 2 - 2);
          if (i1 >= inputShape1) {
            i1 = inputShape1 * 2 - i1 - 2;
          }
        } else if (i1 >= inputShape1) {
          i1 = i1 % (inputShape1 * 2 - 2);
          if (i1 >= inputShape1) {
            i1 = inputShape1 * 2 - i1 - 2;
          }
        }
        const v = dI[i0 * inputStrides0 + i1 * inputStrides1];
        dO[d0 * outputStrides0 + d1 * outputStrides1] = v;
      }
    }
  }

  reflectCopy3d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0, inputShape1, inputShape2] = inputShape;
    const [outputShape0, outputShape1, outputShape2] = outputShape;
    const [inputStrides0, inputStrides1, inputStrides2] = inputStrides;
    const [outputStrides0, outputStrides1, outputStrides2] = outputStrides;
    const [pads0, pads1, pads2] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        for (let d2 = 0; d2 < outputShape2; d2++) {
          let i0 = d0 - pads0,
            i1 = d1 - pads1,
            i2 = d2 - pads2;
          if (i0 < 0) {
            i0 = -i0 % (inputShape0 * 2 - 2);
            if (i0 >= inputShape0) {
              i0 = inputShape0 * 2 - i0 - 2;
            }
          } else if (i0 >= inputShape0) {
            i0 = i0 % (inputShape0 * 2 - 2);
            if (i0 >= inputShape0) {
              i0 = inputShape0 * 2 - i0 - 2;
            }
          }
          if (i1 < 0) {
            i1 = -i1 % (inputShape1 * 2 - 2);
            if (i1 >= inputShape1) {
              i1 = inputShape1 * 2 - i1 - 2;
            }
          } else if (i1 >= inputShape1) {
            i1 = i1 % (inputShape1 * 2 - 2);
            if (i1 >= inputShape1) {
              i1 = inputShape1 * 2 - i1 - 2;
            }
          }
          if (i2 < 0) {
            i2 = -i2 % (inputShape2 * 2 - 2);
            if (i2 >= inputShape2) {
              i2 = inputShape2 * 2 - i2 - 2;
            }
          } else if (i2 >= inputShape2) {
            i2 = i2 % (inputShape2 * 2 - 2);
            if (i2 >= inputShape2) {
              i2 = inputShape2 * 2 - i2 - 2;
            }
          }
          const v =
            dI[i0 * inputStrides0 + i1 * inputStrides1 + i2 * inputStrides2];
          dO[d0 * outputStrides0 + d1 * outputStrides1 + d2 * outputStrides2] =
            v;
        }
      }
    }
  }

  reflectCopy4d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0, inputShape1, inputShape2, inputShape3] = inputShape;
    const [outputShape0, outputShape1, outputShape2, outputShape3] =
      outputShape;
    const [inputStrides0, inputStrides1, inputStrides2, inputStrides3] =
      inputStrides;
    const [outputStrides0, outputStrides1, outputStrides2, outputStrides3] =
      outputStrides;
    const [pads0, pads1, pads2, pads3] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        for (let d2 = 0; d2 < outputShape2; d2++) {
          for (let d3 = 0; d3 < outputShape3; d3++) {
            let i0 = d0 - pads0,
              i1 = d1 - pads1,
              i2 = d2 - pads2,
              i3 = d3 - pads3;
            if (i0 < 0) {
              i0 = -i0 % (inputShape0 * 2 - 2);
              if (i0 >= inputShape0) {
                i0 = inputShape0 * 2 - i0 - 2;
              }
            } else if (i0 >= inputShape0) {
              i0 = i0 % (inputShape0 * 2 - 2);
              if (i0 >= inputShape0) {
                i0 = inputShape0 * 2 - i0 - 2;
              }
            }
            if (i1 < 0) {
              i1 = -i1 % (inputShape1 * 2 - 2);
              if (i1 >= inputShape1) {
                i1 = inputShape1 * 2 - i1 - 2;
              }
            } else if (i1 >= inputShape1) {
              i1 = i1 % (inputShape1 * 2 - 2);
              if (i1 >= inputShape1) {
                i1 = inputShape1 * 2 - i1 - 2;
              }
            }
            if (i2 < 0) {
              i2 = -i2 % (inputShape2 * 2 - 2);
              if (i2 >= inputShape2) {
                i2 = inputShape2 * 2 - i2 - 2;
              }
            } else if (i2 >= inputShape2) {
              i2 = i2 % (inputShape2 * 2 - 2);
              if (i2 >= inputShape2) {
                i2 = inputShape2 * 2 - i2 - 2;
              }
            }
            if (i3 < 0) {
              i3 = -i3 % (inputShape3 * 2 - 2);
              if (i3 >= inputShape3) {
                i3 = inputShape3 * 2 - i3 - 2;
              }
            } else if (i3 >= inputShape3) {
              i3 = i3 % (inputShape3 * 2 - 2);
              if (i3 >= inputShape3) {
                i3 = inputShape3 * 2 - i3 - 2;
              }
            }
            const v =
              dI[
                i0 * inputStrides0 +
                  i1 * inputStrides1 +
                  i2 * inputStrides2 +
                  i3 * inputStrides3
              ];
            dO[
              d0 * outputStrides0 +
                d1 * outputStrides1 +
                d2 * outputStrides2 +
                d3 * outputStrides3
            ] = v;
          }
        }
      }
    }
  }
  reflectCopy5d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0, inputShape1, inputShape2, inputShape3, inputShape4] =
      inputShape;
    const [
      outputShape0,
      outputShape1,
      outputShape2,
      outputShape3,
      outputShape4,
    ] = outputShape;
    const [
      inputStrides0,
      inputStrides1,
      inputStrides2,
      inputStrides3,
      inputStrides4,
    ] = inputStrides;
    const [
      outputStrides0,
      outputStrides1,
      outputStrides2,
      outputStrides3,
      outputStrides4,
    ] = outputStrides;
    const [pads0, pads1, pads2, pads3, pads4] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        for (let d2 = 0; d2 < outputShape2; d2++) {
          for (let d3 = 0; d3 < outputShape3; d3++) {
            for (let d4 = 0; d4 < outputShape4; d4++) {
              let i0 = d0 - pads0,
                i1 = d1 - pads1,
                i2 = d2 - pads2,
                i3 = d3 - pads3,
                i4 = d4 - pads4;
              if (i0 < 0) {
                i0 = -i0 % (inputShape0 * 2 - 2);
                if (i0 >= inputShape0) {
                  i0 = inputShape0 * 2 - i0 - 2;
                }
              } else if (i0 >= inputShape0) {
                i0 = i0 % (inputShape0 * 2 - 2);
                if (i0 >= inputShape0) {
                  i0 = inputShape0 * 2 - i0 - 2;
                }
              }
              if (i1 < 0) {
                i1 = -i1 % (inputShape1 * 2 - 2);
                if (i1 >= inputShape1) {
                  i1 = inputShape1 * 2 - i1 - 2;
                }
              } else if (i1 >= inputShape1) {
                i1 = i1 % (inputShape1 * 2 - 2);
                if (i1 >= inputShape1) {
                  i1 = inputShape1 * 2 - i1 - 2;
                }
              }
              if (i2 < 0) {
                i2 = -i2 % (inputShape2 * 2 - 2);
                if (i2 >= inputShape2) {
                  i2 = inputShape2 * 2 - i2 - 2;
                }
              } else if (i2 >= inputShape2) {
                i2 = i2 % (inputShape2 * 2 - 2);
                if (i2 >= inputShape2) {
                  i2 = inputShape2 * 2 - i2 - 2;
                }
              }
              if (i3 < 0) {
                i3 = -i3 % (inputShape3 * 2 - 2);
                if (i3 >= inputShape3) {
                  i3 = inputShape3 * 2 - i3 - 2;
                }
              } else if (i3 >= inputShape3) {
                i3 = i3 % (inputShape3 * 2 - 2);
                if (i3 >= inputShape3) {
                  i3 = inputShape3 * 2 - i3 - 2;
                }
              }
              if (i4 < 0) {
                i4 = -i4 % (inputShape4 * 2 - 2);
                if (i4 >= inputShape4) {
                  i4 = inputShape4 * 2 - i4 - 2;
                }
              } else if (i4 >= inputShape4) {
                i4 = i4 % (inputShape4 * 2 - 2);
                if (i4 >= inputShape4) {
                  i4 = inputShape4 * 2 - i4 - 2;
                }
              }
              const v =
                dI[
                  i0 * inputStrides0 +
                    i1 * inputStrides1 +
                    i2 * inputStrides2 +
                    i3 * inputStrides3 +
                    i4 * inputStrides4
                ];
              dO[
                d0 * outputStrides0 +
                  d1 * outputStrides1 +
                  d2 * outputStrides2 +
                  d3 * outputStrides3 +
                  d4 * outputStrides4
              ] = v;
            }
          }
        }
      }
    }
  }

  reflectCopy6d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [
      inputShape0,
      inputShape1,
      inputShape2,
      inputShape3,
      inputShape4,
      inputShape5,
    ] = inputShape;
    const [
      outputShape0,
      outputShape1,
      outputShape2,
      outputShape3,
      outputShape4,
      outputShape5,
    ] = outputShape;
    const [
      inputStrides0,
      inputStrides1,
      inputStrides2,
      inputStrides3,
      inputStrides4,
      inputStrides5,
    ] = inputStrides;
    const [
      outputStrides0,
      outputStrides1,
      outputStrides2,
      outputStrides3,
      outputStrides4,
      outputStrides5,
    ] = outputStrides;
    const [pads0, pads1, pads2, pads3, pads4, pads5] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        for (let d2 = 0; d2 < outputShape2; d2++) {
          for (let d3 = 0; d3 < outputShape3; d3++) {
            for (let d4 = 0; d4 < outputShape4; d4++) {
              for (let d5 = 0; d5 < outputShape5; d5++) {
                let i0 = d0 - pads0,
                  i1 = d1 - pads1,
                  i2 = d2 - pads2,
                  i3 = d3 - pads3,
                  i4 = d4 - pads4,
                  i5 = d5 - pads5;
                if (i0 < 0) {
                  i0 = -i0 % (inputShape0 * 2 - 2);
                  if (i0 >= inputShape0) {
                    i0 = inputShape0 * 2 - i0 - 2;
                  }
                } else if (i0 >= inputShape0) {
                  i0 = i0 % (inputShape0 * 2 - 2);
                  if (i0 >= inputShape0) {
                    i0 = inputShape0 * 2 - i0 - 2;
                  }
                }
                if (i1 < 0) {
                  i1 = -i1 % (inputShape1 * 2 - 2);
                  if (i1 >= inputShape1) {
                    i1 = inputShape1 * 2 - i1 - 2;
                  }
                } else if (i1 >= inputShape1) {
                  i1 = i1 % (inputShape1 * 2 - 2);
                  if (i1 >= inputShape1) {
                    i1 = inputShape1 * 2 - i1 - 2;
                  }
                }
                if (i2 < 0) {
                  i2 = -i2 % (inputShape2 * 2 - 2);
                  if (i2 >= inputShape2) {
                    i2 = inputShape2 * 2 - i2 - 2;
                  }
                } else if (i2 >= inputShape2) {
                  i2 = i2 % (inputShape2 * 2 - 2);
                  if (i2 >= inputShape2) {
                    i2 = inputShape2 * 2 - i2 - 2;
                  }
                }
                if (i3 < 0) {
                  i3 = -i3 % (inputShape3 * 2 - 2);
                  if (i3 >= inputShape3) {
                    i3 = inputShape3 * 2 - i3 - 2;
                  }
                } else if (i3 >= inputShape3) {
                  i3 = i3 % (inputShape3 * 2 - 2);
                  if (i3 >= inputShape3) {
                    i3 = inputShape3 * 2 - i3 - 2;
                  }
                }
                if (i4 < 0) {
                  i4 = -i4 % (inputShape4 * 2 - 2);
                  if (i4 >= inputShape4) {
                    i4 = inputShape4 * 2 - i4 - 2;
                  }
                } else if (i4 >= inputShape4) {
                  i4 = i4 % (inputShape4 * 2 - 2);
                  if (i4 >= inputShape4) {
                    i4 = inputShape4 * 2 - i4 - 2;
                  }
                }
                if (i5 < 0) {
                  i5 = -i5 % (inputShape5 * 2 - 2);
                  if (i5 >= inputShape5) {
                    i5 = inputShape5 * 2 - i5 - 2;
                  }
                } else if (i5 >= inputShape5) {
                  i5 = i5 % (inputShape5 * 2 - 2);
                  if (i5 >= inputShape5) {
                    i5 = inputShape5 * 2 - i5 - 2;
                  }
                }
                const v =
                  dI[
                    i0 * inputStrides0 +
                      i1 * inputStrides1 +
                      i2 * inputStrides2 +
                      i3 * inputStrides3 +
                      i4 * inputStrides4 +
                      i5 * inputStrides5
                  ];
                dO[
                  d0 * outputStrides0 +
                    d1 * outputStrides1 +
                    d2 * outputStrides2 +
                    d3 * outputStrides3 +
                    d4 * outputStrides4 +
                    d5 * outputStrides5
                ] = v;
              }
            }
          }
        }
      }
    }
  }

  edgeCopy1d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0] = inputShape;
    const [outputShape0] = outputShape;
    const [inputStrides0] = inputStrides;
    const [outputStrides0] = outputStrides;
    const [pads0] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      let i0 = d0 - pads0;
      if (i0 < 0) {
        i0 = 0;
      } else if (i0 >= inputShape0) {
        i0 = inputShape0 - 1;
      }
      const v = dI[i0 * inputStrides0];
      dO[d0 * outputStrides0] = v;
    }
  }

  edgeCopy2d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0, inputShape1] = inputShape;
    const [outputShape0, outputShape1] = outputShape;
    const [inputStrides0, inputStrides1] = inputStrides;
    const [outputStrides0, outputStrides1] = outputStrides;
    const [pads0, pads1] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        let i0 = d0 - pads0,
          i1 = d1 - pads1;
        if (i0 < 0) {
          i0 = 0;
        } else if (i0 >= inputShape0) {
          i0 = inputShape0 - 1;
        }
        if (i1 < 0) {
          i1 = 0;
        } else if (i1 >= inputShape1) {
          i1 = inputShape1 - 1;
        }
        const v = dI[i0 * inputStrides0 + i1 * inputStrides1];
        dO[d0 * outputStrides0 + d1 * outputStrides1] = v;
      }
    }
  }

  edgeCopy3d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0, inputShape1, inputShape2] = inputShape;
    const [outputShape0, outputShape1, outputShape2] = outputShape;
    const [inputStrides0, inputStrides1, inputStrides2] = inputStrides;
    const [outputStrides0, outputStrides1, outputStrides2] = outputStrides;
    const [pads0, pads1, pads2] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        for (let d2 = 0; d2 < outputShape2; d2++) {
          let i0 = d0 - pads0,
            i1 = d1 - pads1,
            i2 = d2 - pads2;
          if (i0 < 0) {
            i0 = 0;
          } else if (i0 >= inputShape0) {
            i0 = inputShape0 - 1;
          }
          if (i1 < 0) {
            i1 = 0;
          } else if (i1 >= inputShape1) {
            i1 = inputShape1 - 1;
          }
          if (i2 < 0) {
            i2 = 0;
          } else if (i2 >= inputShape2) {
            i2 = inputShape2 - 1;
          }
          const v =
            dI[i0 * inputStrides0 + i1 * inputStrides1 + i2 * inputStrides2];
          dO[d0 * outputStrides0 + d1 * outputStrides1 + d2 * outputStrides2] =
            v;
        }
      }
    }
  }

  edgeCopy4d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0, inputShape1, inputShape2, inputShape3] = inputShape;
    const [outputShape0, outputShape1, outputShape2, outputShape3] =
      outputShape;
    const [inputStrides0, inputStrides1, inputStrides2, inputStrides3] =
      inputStrides;
    const [outputStrides0, outputStrides1, outputStrides2, outputStrides3] =
      outputStrides;
    const [pads0, pads1, pads2, pads3] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        for (let d2 = 0; d2 < outputShape2; d2++) {
          for (let d3 = 0; d3 < outputShape3; d3++) {
            let i0 = d0 - pads0,
              i1 = d1 - pads1,
              i2 = d2 - pads2,
              i3 = d3 - pads3;
            if (i0 < 0) {
              i0 = 0;
            } else if (i0 >= inputShape0) {
              i0 = inputShape0 - 1;
            }
            if (i1 < 0) {
              i1 = 0;
            } else if (i1 >= inputShape1) {
              i1 = inputShape1 - 1;
            }
            if (i2 < 0) {
              i2 = 0;
            } else if (i2 >= inputShape2) {
              i2 = inputShape2 - 1;
            }
            if (i3 < 0) {
              i3 = 0;
            } else if (i3 >= inputShape3) {
              i3 = inputShape3 - 1;
            }
            const v =
              dI[
                i0 * inputStrides0 +
                  i1 * inputStrides1 +
                  i2 * inputStrides2 +
                  i3 * inputStrides3
              ];
            dO[
              d0 * outputStrides0 +
                d1 * outputStrides1 +
                d2 * outputStrides2 +
                d3 * outputStrides3
            ] = v;
          }
        }
      }
    }
  }

  edgeCopy5d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [inputShape0, inputShape1, inputShape2, inputShape3, inputShape4] =
      inputShape;
    const [
      outputShape0,
      outputShape1,
      outputShape2,
      outputShape3,
      outputShape4,
    ] = outputShape;
    const [
      inputStrides0,
      inputStrides1,
      inputStrides2,
      inputStrides3,
      inputStrides4,
    ] = inputStrides;
    const [
      outputStrides0,
      outputStrides1,
      outputStrides2,
      outputStrides3,
      outputStrides4,
    ] = outputStrides;
    const [pads0, pads1, pads2, pads3, pads4] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        for (let d2 = 0; d2 < outputShape2; d2++) {
          for (let d3 = 0; d3 < outputShape3; d3++) {
            for (let d4 = 0; d4 < outputShape4; d4++) {
              let i0 = d0 - pads0,
                i1 = d1 - pads1,
                i2 = d2 - pads2,
                i3 = d3 - pads3,
                i4 = d4 - pads4;
              if (i0 < 0) {
                i0 = 0;
              } else if (i0 >= inputShape0) {
                i0 = inputShape0 - 1;
              }
              if (i1 < 0) {
                i1 = 0;
              } else if (i1 >= inputShape1) {
                i1 = inputShape1 - 1;
              }
              if (i2 < 0) {
                i2 = 0;
              } else if (i2 >= inputShape2) {
                i2 = inputShape2 - 1;
              }
              if (i3 < 0) {
                i3 = 0;
              } else if (i3 >= inputShape3) {
                i3 = inputShape3 - 1;
              }
              if (i4 < 0) {
                i4 = 0;
              } else if (i4 >= inputShape4) {
                i4 = inputShape4 - 1;
              }
              const v =
                dI[
                  i0 * inputStrides0 +
                    i1 * inputStrides1 +
                    i2 * inputStrides2 +
                    i3 * inputStrides3 +
                    i4 * inputStrides4
                ];
              dO[
                d0 * outputStrides0 +
                  d1 * outputStrides1 +
                  d2 * outputStrides2 +
                  d3 * outputStrides3 +
                  d4 * outputStrides4
              ] = v;
            }
          }
        }
      }
    }
  }

  edgeCopy6d(
    dI: DataArrayTypes,
    dO: DataArrayTypes,
    inputShape: ReadonlyArray<number>,
    outputShape: ReadonlyArray<number>,
    inputStrides: ReadonlyArray<number>,
    outputStrides: ReadonlyArray<number>,
    pads: ReadonlyArray<number>
  ) {
    const [
      inputShape0,
      inputShape1,
      inputShape2,
      inputShape3,
      inputShape4,
      inputShape5,
    ] = inputShape;
    const [
      outputShape0,
      outputShape1,
      outputShape2,
      outputShape3,
      outputShape4,
      outputShape5,
    ] = outputShape;
    const [
      inputStrides0,
      inputStrides1,
      inputStrides2,
      inputStrides3,
      inputStrides4,
      inputStrides5,
    ] = inputStrides;
    const [
      outputStrides0,
      outputStrides1,
      outputStrides2,
      outputStrides3,
      outputStrides4,
      outputStrides5,
    ] = outputStrides;
    const [pads0, pads1, pads2, pads3, pads4, pads5] = pads;
    for (let d0 = 0; d0 < outputShape0; d0++) {
      for (let d1 = 0; d1 < outputShape1; d1++) {
        for (let d2 = 0; d2 < outputShape2; d2++) {
          for (let d3 = 0; d3 < outputShape3; d3++) {
            for (let d4 = 0; d4 < outputShape4; d4++) {
              for (let d5 = 0; d5 < outputShape5; d5++) {
                let i0 = d0 - pads0,
                  i1 = d1 - pads1,
                  i2 = d2 - pads2,
                  i3 = d3 - pads3,
                  i4 = d4 - pads4,
                  i5 = d5 - pads5;
                if (i0 < 0) {
                  i0 = 0;
                } else if (i0 >= inputShape0) {
                  i0 = inputShape0 - 1;
                }
                if (i1 < 0) {
                  i1 = 0;
                } else if (i1 >= inputShape1) {
                  i1 = inputShape1 - 1;
                }
                if (i2 < 0) {
                  i2 = 0;
                } else if (i2 >= inputShape2) {
                  i2 = inputShape2 - 1;
                }
                if (i3 < 0) {
                  i3 = 0;
                } else if (i3 >= inputShape3) {
                  i3 = inputShape3 - 1;
                }
                if (i4 < 0) {
                  i4 = 0;
                } else if (i4 >= inputShape4) {
                  i4 = inputShape4 - 1;
                }
                if (i5 < 0) {
                  i5 = 0;
                } else if (i5 >= inputShape5) {
                  i5 = inputShape5 - 1;
                }
                const v =
                  dI[
                    i0 * inputStrides0 +
                      i1 * inputStrides1 +
                      i2 * inputStrides2 +
                      i3 * inputStrides3 +
                      i4 * inputStrides4 +
                      i5 * inputStrides5
                  ];
                dO[
                  d0 * outputStrides0 +
                    d1 * outputStrides1 +
                    d2 * outputStrides2 +
                    d3 * outputStrides3 +
                    d4 * outputStrides4 +
                    d5 * outputStrides5
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
      factory: () => new CPUPad11(),
    },
  ];
}
