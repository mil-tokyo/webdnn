import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrInt } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { arrayProd } from "../../../../util";

class InstanceNormalization extends OperatorImpl {
  epsilon!: number;

  constructor() {
    super("cpu");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.epsilon = getAttrInt(attribute, "epsilon", 1e-5);
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const [input, scale, bias] = inputs;
    const reductionLength = arrayProd(input.dims.slice(2)),
      output = context.emptyTensor(input.dims, input.dataType),
      dI = input.data,
      dO = output.data,
      dS = scale.data,
      dB = bias.data;
    const [dimBatch, dimCh] = input.dims;
    const [strideBatch, strideCh] = input.strides;
    for (let batch = 0; batch < dimBatch; batch++) {
      for (let ch = 0; ch < dimCh; ch++) {
        const ofs = batch * strideBatch + ch * strideCh;
        let sum = 0.0;
        let sqsum = 0.0;
        for (let r = 0; r < reductionLength; r++) {
          const v = dI[ofs + r];
          sum += v;
          sqsum += v * v;
        }
        const mean = sum / reductionLength;
        const variance = sqsum / reductionLength - mean * mean;
        const invstd = 1 / Math.sqrt(variance + this.epsilon);
        const chscale = dS[ch] * invstd;
        const chbias = -mean * chscale + dB[ch];
        for (let r = 0; r < reductionLength; r++) {
          dO[ofs + r] = dI[ofs + r] * chscale + chbias;
        }
      }
    }
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "InstanceNormalization",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new InstanceNormalization(),
    },
  ];
}
