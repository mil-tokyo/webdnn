import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { ConvTranspose } from "../../../base/convtranspose";

class CpuConvTranspose extends ConvTranspose {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const inputX = inputs[0],
      inputW = inputs[1],
      inputB = inputs[2];
    // TODO: 2D以外対応
    if (inputX.ndim !== 4) {
      throw new Error("ConvTranspose other than 2D is not yet supported");
    }
    const {
        batch,
        dilations,
        group,
        kernelShape,
        pads,
        strides,
        inShape,
        outShape,
        chIn,
        chInPerGroup,
        chOut,
        chOutPerGroup,
      } = this.calcShape(inputX.dims, inputW.dims),
      // group, batch, inShape[0], inShape[1], chInPerGroup
      inputTransposeData = new Float32Array(
        chIn * batch * inShape[0] * inShape[1]
      ),
      // group, chOutPerGroup, kernelShape[0], kernelShape[1], chInPerGroup
      weightTransposeData = new Float32Array(
        chOut * kernelShape[0] * kernelShape[1] * chInPerGroup
      ),
      // group, batch, inShape[0], inShape[1], chOutPerGroup, kernelShape[0], kernelShape[1]
      matmulData = new Float32Array(
        chOut *
          batch *
          inShape[0] *
          inShape[1] *
          kernelShape[0] *
          kernelShape[1]
      ),
      col2ImData = new Float32Array(batch * chOut * outShape[0] * outShape[1]);
    this.transposeInput(
      inputX.data as Float32Array,
      inputTransposeData,
      group,
      batch,
      inShape[0] * inShape[1],
      chInPerGroup
    );
    this.transposeWeight(
      inputW.data as Float32Array,
      weightTransposeData,
      group,
      chInPerGroup,
      chOutPerGroup,
      kernelShape[0] * kernelShape[1]
    );
    this.matmul(
      inputTransposeData,
      weightTransposeData,
      matmulData,
      group,
      batch * inShape[0] * inShape[1],
      chOutPerGroup * kernelShape[0] * kernelShape[1],
      chInPerGroup
    );
    this.col2im(
      matmulData,
      col2ImData,
      batch,
      dilations,
      group,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      chOutPerGroup
    );
    if (inputB) {
      this.bias(
        inputB.data as Float32Array,
        col2ImData,
        batch,
        chOut,
        outShape[0] * outShape[1]
      );
    }
    const output = context.emptyTensor(
      [batch, chOut, outShape[0], outShape[1]],
      "float32",
      col2ImData
    );
    return [output];
  }

  private col2im(
    dI: Float32Array,
    dY: Float32Array,
    batch: number,
    dilations: number[],
    group: number,
    kernelShape: number[],
    pads: number[],
    strides: number[],
    inShape: number[],
    outShape: number[],
    chOutPerGroup: number
  ): void {
    let idx = 0;
    // dI: group, batch, inShape[0], inShape[1], chOutPerGroup, kernelShape[0], kernelShape[1]
    // dY: batch, group, chOutPerGroup, outShape[0], outShape[1]
    for (let b = 0; b < batch; b++) {
      for (let g = 0; g < group; g++) {
        for (let co = 0; co < chOutPerGroup; co++) {
          for (let o0 = 0; o0 < outShape[0]; o0++) {
            for (let o1 = 0; o1 < outShape[1]; o1++) {
              let v = 0;
              for (let k0 = 0; k0 < kernelShape[0]; k0++) {
                for (let k1 = 0; k1 < kernelShape[1]; k1++) {
                  const i0s = o0 + pads[0] - k0 * dilations[0];
                  const i1s = o1 + pads[1] - k1 * dilations[1];
                  if (i0s % strides[0] !== 0 || i1s % strides[1] !== 0) {
                    continue;
                  }

                  const i0 = i0s / strides[0];
                  const i1 = i1s / strides[1];
                  if (
                    i0 < 0 ||
                    i0 >= inShape[0] ||
                    i1 < 0 ||
                    i1 >= inShape[1]
                  ) {
                    continue;
                  }
                  v +=
                    dI[
                      (((((g * batch + b) * inShape[0] + i0) * inShape[1] +
                        i1) *
                        chOutPerGroup +
                        co) *
                        kernelShape[0] +
                        k0) *
                        kernelShape[1] +
                        k1
                    ];
                }
              }
              dY[idx++] = v;
            }
          }
        }
      }
    }
  }

  private matmul(
    dTX: Float32Array,
    dTW: Float32Array,
    dI: Float32Array,
    group: number,
    bin: number,
    cks: number,
    chInPerGroup: number
  ) {
    // dTX(group, batch*inShape[0]*inShape[1]=bin, chInPerGroup) * dTW(group, chOutPerGroup*kernelShape[0]*kernelShape[1]=cks, chInPerGroup) -> dI(group, bin, cks)
    for (let g = 0; g < group; g++) {
      for (let y = 0; y < bin; y++) {
        for (let x = 0; x < cks; x++) {
          let s = 0;
          const dtxofs = (g * bin + y) * chInPerGroup;
          const dtwofs = (g * cks + x) * chInPerGroup;
          for (let ip = 0; ip < chInPerGroup; ip++) {
            s += dTX[dtxofs + ip] * dTW[dtwofs + ip];
          }
          dI[(g * bin + y) * cks + x] = s;
        }
      }
    }
  }

  private transposeInput(
    dX: Float32Array,
    dTX: Float32Array,
    group: number,
    batch: number,
    inarea: number,
    chInPerGroup: number
  ) {
    // dX(batch, group, chInPerGroup, inShape[0], inShape[1]) -> dTX(group, batch, inShape[0], inShape[1], chInPerGroup)
    let idx = 0;
    for (let g = 0; g < group; g++) {
      for (let b = 0; b < batch; b++) {
        for (let x = 0; x < inarea; x++) {
          for (let c = 0; c < chInPerGroup; c++) {
            dTX[idx++] = dX[((b * group + g) * chInPerGroup + c) * inarea + x];
          }
        }
      }
    }
  }

  private transposeWeight(
    dW: Float32Array,
    dTW: Float32Array,
    group: number,
    chInPerGroup: number,
    chOutPerGroup: number,
    karea: number
  ) {
    // dW(group, chInPerGroup, chOutPerGroup, kernelShape[0], kernelShape[1]) -> dTW(group, chOutPerGroup, kernelShape[0], kernelShape[1], cInPerGroup)
    let idx = 0;
    for (let g = 0; g < group; g++) {
      for (let co = 0; co < chOutPerGroup; co++) {
        for (let k = 0; k < karea; k++) {
          for (let ci = 0; ci < chInPerGroup; ci++) {
            dTW[idx++] =
              dW[((g * chInPerGroup + ci) * chOutPerGroup + co) * karea + k];
          }
        }
      }
    }
  }

  private bias(
    dB: Float32Array,
    dO: Float32Array,
    batch: number,
    chOut: number,
    outarea: number
  ) {
    let idx = 0;
    for (let b = 0; b < batch; b++) {
      for (let c = 0; c < chOut; c++) {
        for (let x = 0; x < outarea; x++) {
          dO[idx++] += dB[c];
        }
      }
    }
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "ConvTranspose",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CpuConvTranspose(),
    },
  ];
}
