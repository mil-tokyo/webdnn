import { OperatorImpl } from "../operatorImpl";
import { Tensor } from "../../interface/core/tensor";
import { onnx } from "onnx-proto";
import { getAttrString } from "../operatorUtil";
import { Backend } from "../../interface/core/constants";
import { CPUTensor } from "../../interface/backend/cpu/cpuTensor";

type PadMode = "constant" | "reflect" | "edge";

/*
 * Opset 11
 * opset 2は互換性なし
 */
export abstract class Pad11 extends OperatorImpl {
  mode!: PadMode;

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.mode = getAttrString(attribute, "mode", "constant") as PadMode;
  }

  getTensorBackendRequirement(
    nInputs: number,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    nOutputs: number
  ): (Backend | null)[] {
    if (nInputs === 2) {
      return [this.backend, "cpu"];
    } else {
      return [this.backend, "cpu", "cpu"];
    }
  }

  protected calcShape(
    input: Tensor,
    padTensor: CPUTensor
  ): { outputShape: number[]; pads: number[] } {
    const outputShape: number[] = [];
    const pads: number[] = Array.from(padTensor.data);
    for (let i = 0; i < input.ndim; i++) {
      outputShape.push(input.dims[i] + pads[i] + pads[i + input.ndim]);
    }
    return { outputShape, pads };
  }
}
