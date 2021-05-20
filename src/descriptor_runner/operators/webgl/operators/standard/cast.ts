import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNWebGLContext } from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { getAttrInt } from "../../../operatorUtil";
import { OperatorEntry } from "../../../../interface/core/operator";

class Cast extends OperatorImpl {
  to!: onnx.TensorProto.DataType;

  constructor() {
    super("webgl");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.to = getAttrInt(attribute, "to", onnx.TensorProto.DataType.FLOAT);
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0];
    // 現状、trivialなfloat32->float32のキャストのみ通す
    if (input.dataType !== "float32") {
      throw new Error(`Cast: input must be float32`);
    }
    if (this.to !== onnx.TensorProto.DataType.FLOAT) {
      throw new Error(`Cast: output must be float32`);
    }

    return [input.alias(input.dims)];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Cast",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new Cast(),
    },
  ];
}
