import { WebDNNWebGLContext } from "../../../../interface/backend/webgl/webglContext";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Flatten } from "../../../base/flatten";

class WebGLFlatten extends Flatten {
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

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Flatten",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLFlatten(),
    },
  ];
}
