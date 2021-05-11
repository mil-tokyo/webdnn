import { WebDNNWebGLContext } from "../../../../interface/backend/webgl/webglContext";
import { Backend } from "../../../../interface/core/constants";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Reshape5 } from "../../../base/reshape5";

export class WebGLReshape5 extends Reshape5 {
  constructor() {
    super("webgl");
  }

  getTensorBackendRequirement(
    nInputs: number,
    nOutputs: number
  ): (Backend | null)[] {
    return [this.backend, "cpu"];
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    const input = inputs[0];
    const shapeTensor = inputs[1];
    if (!context.cpuContext.isCPUTensor(shapeTensor)) {
      throw new Error(`Reshape: shapeTensor is not on cpu.`);
    }
    if (!context.isWebGLTensor(input)) {
      throw new Error("Reshape: input is not on webgl.");
    }
    const computedShape = this.calcShape(input, shapeTensor);

    return [input.alias(computedShape)];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Reshape",
      backend: "webgl",
      opsetMin: 5,
      factory: () => new WebGLReshape5(),
    },
  ];
}
