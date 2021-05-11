import { WebDNNWebGPUContext } from "../../../../interface/backend/webgpu/webgpuContext";
import { WebGPUTensor } from "../../../../interface/backend/webgpu/webgpuTensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Gemm } from "../../../base/gemm";
import { broadcastUni } from "../../../operatorUtil";
import { webgpuShaders } from "../../shaders";

export class WebGPUGemm extends Gemm {
  constructor() {
    super("webgpu");
  }

  async run(context: WebDNNWebGPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGPUTensorArray(inputs);
    const inputA = inputs[0];
    const inputB = inputs[1];
    const inputC = inputs[2];
    if (inputC) {
      return this.runWithC(context, inputA, inputB, inputC);
    } else {
      throw new Error();
    }
  }

  async runWithC(
    context: WebDNNWebGPUContext,
    inputA: WebGPUTensor,
    inputB: WebGPUTensor,
    inputC: WebGPUTensor
  ): Promise<WebGPUTensor[]> {
    if (inputA.dataType !== "float32") {
      throw new Error();
    }
    const {
      m,
      n,
      k,
      strideA: [strideA0, strideA1],
      strideB: [strideB0, strideB1],
    } = this.calcShape(inputA.dims, inputB.dims);
    const [strideC0, strideC1] = broadcastUni([m, n], inputC.dims);

    const outputTensor = context.emptyTensor([m, n], "float32");

    const shaderName = "gemm";

    if (!context.hasPipeline(shaderName)) {
      context.createPipeline(shaderName, webgpuShaders["gemm"], 5);
    }

    await context.run({
      pipelineName: shaderName,
      tensors: [inputA, inputB, inputC, outputTensor],
      meta: {
        elements: [
          { value: m, type: "uint32" },
          { value: n, type: "uint32" },
          { value: k, type: "uint32" },
          { value: strideA0, type: "uint32" },
          { value: strideA1, type: "uint32" },
          { value: strideB0, type: "uint32" },
          { value: strideB1, type: "uint32" },
          { value: strideC0, type: "uint32" },
          { value: strideC1, type: "uint32" },
          { value: this.alpha, type: "float32" },
          { value: this.beta, type: "float32" },
        ],
      },
      workGroups: { x: 256 / 8, y: 256 / 8, z: 1 },
    });

    return [outputTensor];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Gemm",
      backend: "webgpu",
      opsetMin: 1,
      factory: () => new WebGPUGemm(),
    },
  ];
}
