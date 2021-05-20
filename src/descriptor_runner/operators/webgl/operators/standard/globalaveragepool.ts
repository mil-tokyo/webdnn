import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNWebGLContext } from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { averagepool } from "../../rawcomputation/averagepool";
import { OperatorEntry } from "../../../../interface/core/operator";

// Version 11
export class WebGLGlobalAveragePool extends OperatorImpl {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const inputX = inputs[0];
    // TODO: 2D以外対応
    if (inputX.ndim !== 4) {
      throw new Error("MaxPool other than 2D is not yet supported");
    }
    if (inputX.dimPerPixel !== 1) {
      throw new Error();
    }

    const batch = inputX.dims[0],
      ch = inputX.dims[1],
      inShape = [inputX.dims[2], inputX.dims[3]],
      outShape = [1, 1],
      output = context.emptyTensor(
        [batch, ch, outShape[0], outShape[1]],
        "float32",
        1
      );
    await averagepool(
      context,
      inputX,
      output,
      true, // わずかに計算量が減る
      batch,
      inShape,
      [0, 0, 0, 0],
      [1, 1],
      inShape,
      outShape,
      ch
    );
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "GlobalAveragePool",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLGlobalAveragePool(),
    },
  ];
}
