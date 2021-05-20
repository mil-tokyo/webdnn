import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNWebGPUContext } from "../../../../interface/backend/webgpu/webgpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { webgpuShaders } from "../../shaders";
import { OperatorEntry } from "../../../../interface/core/operator";

export class WebGPUUnary extends OperatorImpl {
  constructor(public shaderName: string, private shaderBinary: Uint32Array) {
    super("webgpu");
  }

  async run(context: WebDNNWebGPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    const input = inputs[0];
    if (input.dataType !== "float32") {
      throw new Error();
    }
    const outputTensor = context.emptyTensor(input.dims, "float32");

    if (!context.hasPipeline(this.shaderName)) {
      context.createPipeline(this.shaderName, this.shaderBinary, 3);
    }

    await context.run({
      pipelineName: this.shaderName,
      tensors: [input, outputTensor],
      meta: {
        elements: [{ value: input.length, type: "uint32" }],
      },
      workGroups: { x: 4096 / 64, y: 1, z: 1 },
    });

    return [outputTensor];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Relu",
      backend: "webgpu",
      opsetMin: 1,
      factory: () => new WebGPUUnary("relu", webgpuShaders.relu),
    },
  ];
}
