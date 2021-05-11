import { WebDNNWebGLContext } from "../../../../interface/backend/webgl/webglContext";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Unsqueeze } from "../../../base/unsqueeze";

export class WebGLUnsqueeze extends Unsqueeze {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0];
    const computedShape = this.calcShape(input);

    return [input.alias(computedShape)];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Unsqueeze",
      backend: "webgl",
      opsetMin: 1,
      opsetMax: 11,
      factory: () => new WebGLUnsqueeze(),
    },
  ];
}
