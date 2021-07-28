import { WebDNNWebGLContext } from "../../../../interface/backend/webgl/webglContext";
import { Backend } from "../../../../interface/core/constants";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Squeeze1, Squeeze13 } from "../../../base/squeeze";

export class WebGLSqueeze1 extends Squeeze1 {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0],
      computedShape = this.calcShape(input);

    return [input.alias(computedShape)];
  }
}

export class WebGLSqueeze13 extends Squeeze13 {
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
    const input = inputs[0],
      axes = inputs[1];
    if (!context.cpuContext.isCPUTensor(axes)) {
      throw new Error(`Unsqueeze: axes is not on cpu.`);
    }
    if (!context.isWebGLTensor(input)) {
      throw new Error("Unsqueeze: input is not on webgl.");
    }
    const computedShape = this.calcShape(input, axes);

    return [input.alias(computedShape)];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Squeeze",
      backend: "webgl",
      opsetMin: 13,
      factory: () => new WebGLSqueeze13(),
    },
    {
      opType: "Squeeze",
      backend: "webgl",
      opsetMin: 1,
      opsetMax: 13,
      factory: () => new WebGLSqueeze1(),
    },
  ];
}
