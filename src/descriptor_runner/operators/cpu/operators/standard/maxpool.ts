import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { MaxPool } from "../../../base/maxpool";

// version 11
class CpuMaxPool extends MaxPool {
  constructor() {
    super("cpu");
  }

  async run(
    context: WebDNNCPUContext,
    inputs: Tensor[],
    nOutputs: number
  ): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const inputX = inputs[0];
    if (nOutputs !== 1) {
      // TODO: Indicesの出力対応
      throw new Error("MaxPool: output indices is not yet supported");
    }
    // TODO: 2D以外対応
    if (inputX.ndim !== 4) {
      throw new Error("MaxPool other than 2D is not yet supported");
    }
    const {
      batch,
      dilations,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      ch,
    } = this.calcShape(inputX.dims);
    const outputData = new Float32Array(batch * outShape[0] * outShape[1] * ch);
    this.maxpool(
      inputX.data as Float32Array,
      outputData,
      batch,
      dilations,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      ch
    );
    const output = context.emptyTensor(
      [batch, ch, outShape[0], outShape[1]],
      "float32",
      outputData
    );
    return [output];
  }

  private maxpool(
    dX: Float32Array,
    dI: Float32Array,
    batch: number,
    dilations: number[],
    kernelShape: number[],
    pads: number[],
    strides: number[],
    inShape: number[],
    outShape: number[],
    ch: number
  ): void {
    /*
      batch,
      dilations,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      ch, */
    let idx = 0;
    for (let b = 0; b < batch; b++) {
      for (let c = 0; c < ch; c++) {
        for (let oy = 0; oy < outShape[0]; oy++) {
          for (let ox = 0; ox < outShape[1]; ox++) {
            let mv = -Infinity;
            for (let ky = 0; ky < kernelShape[0]; ky++) {
              for (let kx = 0; kx < kernelShape[1]; kx++) {
                const iny = oy * strides[0] - pads[0] + ky * dilations[0];
                const inx = ox * strides[1] - pads[1] + kx * dilations[1];
                if (
                  iny >= 0 &&
                  iny < inShape[0] &&
                  inx >= 0 &&
                  inx < inShape[1]
                ) {
                  const xidx =
                    ((b * ch + c) * inShape[0] + iny) * inShape[1] + inx;
                  const v = dX[xidx];
                  if (v > mv) {
                    mv = v;
                    // max position: xidxを出力
                  }
                }
              }
            }

            dI[idx++] = mv;
          }
        }
      }
    }
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "MaxPool",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CpuMaxPool(),
    },
  ];
}
