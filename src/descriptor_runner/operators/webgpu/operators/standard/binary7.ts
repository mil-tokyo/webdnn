import { OperatorImpl } from "../../../operatorImpl";
import {
  WebDNNWebGPUContext,
  WebGPUMetaBufferContentElement,
} from "../../../../interface/backend/webgpu/webgpuContext";
import { WebGPUTensor } from "../../../../interface/backend/webgpu/webgpuTensor";
import { Tensor } from "../../../../interface/core/tensor";
import { arrayEqual, broadcastMulti } from "../../../operatorUtil";
import { OperatorEntry } from "../../../../interface/core/operator";
import { webgpuShaders } from "../../shaders";

class WebGPUBinary7 extends OperatorImpl {
  constructor(
    public elementwiseShaderName: string,
    private elementwiseShaderBinary: Uint32Array,
    public broadcastShaderNames: string[],
    private broadcastShaderBinaries: Uint32Array[]
  ) {
    super("webgpu");
  }

  async run(context: WebDNNWebGPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGPUTensorArray(inputs);
    const inputA = inputs[0],
      inputB = inputs[1];
    if (inputA.dataType !== "float32" || inputB.dataType !== "float32") {
      throw new Error();
    }
    if (arrayEqual(inputA.dims, inputB.dims)) {
      return this.runElementwise(context, inputA, inputB);
    }
    return this.runBroadcast(context, inputA, inputB);
  }

  private async runElementwise(
    context: WebDNNWebGPUContext,
    inputA: WebGPUTensor,
    inputB: WebGPUTensor
  ) {
    const outputTensor = context.emptyTensor(inputA.dims, "float32");

    if (!context.hasPipeline(this.elementwiseShaderName)) {
      context.createPipeline(
        this.elementwiseShaderName,
        this.elementwiseShaderBinary,
        4
      );
    }

    await context.run({
      pipelineName: this.elementwiseShaderName,
      tensors: [inputA, inputB, outputTensor],
      meta: {
        elements: [{ value: inputA.length, type: "uint32" }],
      },
      workGroups: {
        x: Math.ceil(Math.min(outputTensor.length, 4096) / 64),
        y: 1,
        z: 1,
      },
    });

    return [outputTensor];
  }

  private async runBroadcast(
    context: WebDNNWebGPUContext,
    inputA: WebGPUTensor,
    inputB: WebGPUTensor
  ) {
    const { dims: outShape, allStrides: inAllStrides } = broadcastMulti([
        inputA.dims,
        inputB.dims,
      ]),
      outputTensor = context.emptyTensor(outShape, "float32"),
      outNDim = outputTensor.ndim,
      metaElements: WebGPUMetaBufferContentElement[] = [
        { value: outputTensor.length, type: "uint32" },
      ];
    for (let dim = 0; dim < outNDim; dim++) {
      metaElements.push({ value: outShape[dim], type: "uint32" });
    }
    for (let dim = 0; dim < outNDim; dim++) {
      metaElements.push({ value: inAllStrides[0][dim], type: "uint32" });
    }
    for (let dim = 0; dim < outNDim; dim++) {
      metaElements.push({ value: inAllStrides[1][dim], type: "uint32" });
    }

    if (!context.hasPipeline(this.broadcastShaderNames[outNDim])) {
      context.createPipeline(
        this.broadcastShaderNames[outNDim],
        this.broadcastShaderBinaries[outNDim],
        4
      );
    }

    await context.run({
      pipelineName: this.broadcastShaderNames[outNDim],
      tensors: [inputA, inputB, outputTensor],
      meta: {
        elements: metaElements,
      },
      workGroups: {
        x: Math.ceil(Math.min(outputTensor.length, 4096) / 64),
        y: 1,
        z: 1,
      },
    });

    return [outputTensor];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    // Add, Sub, Mul, Div, Pow: opset under 7 requires explicit broadcast flag
    {
      opType: "Add",
      backend: "webgpu",
      opsetMin: 7,
      factory: () =>
        new WebGPUBinary7(
          "binary_elementwise_add",
          webgpuShaders.binary_elementwise_add,
          [
            "binary_broadcast_add_0d",
            "binary_broadcast_add_1d",
            "binary_broadcast_add_2d",
            "binary_broadcast_add_3d",
            "binary_broadcast_add_4d",
          ],
          [
            webgpuShaders.binary_broadcast_add_0d,
            webgpuShaders.binary_broadcast_add_1d,
            webgpuShaders.binary_broadcast_add_2d,
            webgpuShaders.binary_broadcast_add_3d,
            webgpuShaders.binary_broadcast_add_4d,
          ]
        ),
    },
  ];
}
