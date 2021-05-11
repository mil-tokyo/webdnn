import { WebDNNWebGPUContext } from "../../../../interface/backend/webgpu/webgpuContext";
import { WebGPUTensor } from "../../../../interface/backend/webgpu/webgpuTensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { Conv } from "../../../base/conv";
import { webgpuShaders } from "../../shaders";

class WebGPUConv extends Conv {
  constructor() {
    super("webgpu");
  }

  async run(context: WebDNNWebGPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGPUTensorArray(inputs);
    const inputX = inputs[0];
    const inputW = inputs[1];
    const inputB = inputs[2];
    // TODO: 2D以外対応
    if (inputX.ndim !== 4) {
      throw new Error("Conv other than 2D is not yet supported");
    }
    const {
      batch,
      dilations,
      group,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      chIn,
      chInPerGroup,
      chOut,
      chOutPerGroup,
    } = this.calcShape(inputX.dims, inputW.dims);
    const im2colData = context.emptyTensor([
      group *
        batch *
        outShape[0] *
        outShape[1] *
        chInPerGroup *
        kernelShape[0] *
        kernelShape[1],
    ]);
    await this.im2col(
      context,
      inputX,
      im2colData,
      batch,
      dilations,
      group,
      kernelShape,
      pads,
      strides,
      inShape,
      outShape,
      chIn,
      chInPerGroup,
      chOut,
      chOutPerGroup
    );
    const matmulData = context.emptyTensor([
      group * batch * outShape[0] * outShape[1] * chOutPerGroup,
    ]);
    await this.matmul(
      context,
      im2colData,
      inputW,
      matmulData,
      group,
      batch * outShape[0] * outShape[1],
      chInPerGroup * kernelShape[0] * kernelShape[1],
      chOutPerGroup
    );
    im2colData.dispose();
    const output = context.emptyTensor([
      batch,
      chOut,
      outShape[0],
      outShape[1],
    ]);
    if (inputB) {
      const transposeData = context.emptyTensor([
        batch * chOut * outShape[0] * outShape[1],
      ]);

      await this.transpose(
        context,
        matmulData,
        transposeData,
        group,
        batch,
        outShape[0] * outShape[1],
        chOutPerGroup
      );
      matmulData.dispose();
      await this.bias(
        context,
        transposeData,
        inputB,
        output,
        batch,
        chOut,
        outShape[0] * outShape[1]
      );
      transposeData.dispose();
    } else {
      await this.transpose(
        context,
        matmulData,
        output,
        group,
        batch,
        outShape[0] * outShape[1],
        chOutPerGroup
      );
      matmulData.dispose();
    }
    return [output];
  }

  private async im2col(
    context: WebDNNWebGPUContext,
    dX: WebGPUTensor,
    dI: WebGPUTensor,
    batch: number,
    dilations: number[],
    group: number,
    kernelShape: number[],
    pads: number[],
    strides: number[],
    inShape: number[],
    outShape: number[],
    chIn: number,
    chInPerGroup: number,
    chOut: number,
    chOutPerGroup: number
  ) {
    const shaderName = "conv_im2col";

    if (!context.hasPipeline(shaderName)) {
      context.createPipeline(shaderName, webgpuShaders[shaderName], 3);
    }

    await context.run({
      pipelineName: shaderName,
      tensors: [dX, dI],
      meta: {
        elements: [
          { value: group, type: "int32" },
          { value: batch, type: "int32" },
          { value: outShape[0], type: "int32" },
          { value: outShape[1], type: "int32" },
          { value: chInPerGroup, type: "int32" },
          { value: kernelShape[0], type: "int32" },
          { value: kernelShape[1], type: "int32" },
          { value: strides[0], type: "int32" },
          { value: strides[1], type: "int32" },
          { value: pads[0], type: "int32" },
          { value: pads[1], type: "int32" },
          { value: dilations[0], type: "int32" },
          { value: dilations[1], type: "int32" },
          { value: inShape[0], type: "int32" },
          { value: inShape[1], type: "int32" },
          { value: chIn, type: "int32" },
        ],
      },
      workGroups: { x: 4096 / 64, y: 1, z: 1 },
    });
  }

  private async matmul(
    context: WebDNNWebGPUContext,
    dI: WebGPUTensor,
    dW: WebGPUTensor,
    dT: WebGPUTensor,
    group: number,
    bout: number,
    cinkhkw: number,
    chOutPerGroup: number
  ) {
    const shaderName = "conv_matmul";

    if (!context.hasPipeline(shaderName)) {
      context.createPipeline(shaderName, webgpuShaders[shaderName], 4);
    }

    await context.run({
      pipelineName: shaderName,
      tensors: [dI, dW, dT],
      meta: {
        elements: [
          { value: group, type: "int32" },
          { value: bout, type: "int32" },
          { value: chOutPerGroup, type: "int32" },
          { value: cinkhkw, type: "int32" },
        ],
      },
      workGroups: { x: 4096 / 64, y: 1, z: 1 },
    });
  }

  private async transpose(
    context: WebDNNWebGPUContext,
    dT: WebGPUTensor,
    dO: WebGPUTensor,
    group: number,
    batch: number,
    outarea: number,
    chOutPerGroup: number
  ) {
    const shaderName = "conv_transpose";

    if (!context.hasPipeline(shaderName)) {
      context.createPipeline(shaderName, webgpuShaders[shaderName], 3);
    }

    await context.run({
      pipelineName: shaderName,
      tensors: [dT, dO],
      meta: {
        elements: [
          { value: group, type: "int32" },
          { value: batch, type: "int32" },
          { value: outarea, type: "int32" },
          { value: chOutPerGroup, type: "int32" },
        ],
      },
      workGroups: { x: 4096 / 64, y: 1, z: 1 },
    });
  }

  private async bias(
    context: WebDNNWebGPUContext,
    dI: WebGPUTensor,
    dB: WebGPUTensor,
    dO: WebGPUTensor,
    batch: number,
    chOut: number,
    outarea: number
  ) {
    const shaderName = "conv_bias";

    if (!context.hasPipeline(shaderName)) {
      context.createPipeline(shaderName, webgpuShaders[shaderName], 4);
    }

    await context.run({
      pipelineName: shaderName,
      tensors: [dI, dB, dO],
      meta: {
        elements: [
          { value: batch, type: "int32" },
          { value: chOut, type: "int32" },
          { value: outarea, type: "int32" },
        ],
      },
      workGroups: { x: 4096 / 64, y: 1, z: 1 },
    });
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Conv",
      backend: "webgpu",
      opsetMin: 1,
      factory: () => new WebGPUConv(),
    },
  ];
}
