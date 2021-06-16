import { AveragePool } from "../../../base/averagepool";
import { averagepool } from "../../rawcomputation/averagepool";
import { WebDNNWebGLContext } from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

// Version 1, 7, 10, 11+
class WebGLAveragePool extends AveragePool {
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

    const { batch, kernelShape, pads, strides, inShape, outShape, ch } =
        this.calcShape(inputX.dims),
      output = context.emptyTensor(
        [batch, ch, outShape[0], outShape[1]],
        "float32",
        { dimPerPixel: 1 }
      );
    await averagepool(
      context,
      inputX,
      output,
      this.countIncludePad,
      batch,
      kernelShape,
      pads,
      strides,
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
      opType: "AveragePool",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLAveragePool(),
    },
  ];
}
