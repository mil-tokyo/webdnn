# Use RGBA channel in WebGL2

from typing import Dict, Iterable, List, Optional
import onnx
from webdnn.optimization_pass_result_webgl import OptimizationPassResultWebGL
from webdnn.optimization_pass import OptimizationPass, OptimizationPassResult
from webdnn.onnx_util import tensor_proto_to_numpy, get_attr_int
from webdnn.operator_shader_webgl import OperatorShaderWebGL

SHADER_CODE = """import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { WebGLTensor } from "../../../../interface/backend/webgl/webglTensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Tensor } from "../../../../interface/core/tensor";
import { arange } from "../../../../util";
import { Conv } from "../../../base/conv";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenOutputVec4,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorNDGetVec4,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";

const IM2COL_SPLIT_NUMEL = 4194304;

class WebGLConvReshapeWebGL extends Conv {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const inputX = inputs[0],
      inputW = inputs[1],
      inputB = inputs[2];
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
    if (inputX.dimPerPixel !== 1 || (inputB && inputB.dimPerPixel !== 1)) {
      throw new Error();
    }
    // Wのdimperpixelは分岐
    // 場合分け
    let matmulData: WebGLTensor;

    const im2colLengthPerOutRow =
      group *
      batch *
      outShape[1] *
      chInPerGroup *
      kernelShape[0] *
      kernelShape[1];
    const im2colLength = im2colLengthPerOutRow * outShape[0];
    const cinkhkw = chInPerGroup * kernelShape[0] * kernelShape[1];
    // const gbout = group * batch * outShape[0] * outShape[1];
    const chunkCount = Math.ceil(im2colLength / IM2COL_SPLIT_NUMEL);
    const defaultChunkSize = Math.ceil(outShape[0] / chunkCount);
    const chunkInfos: { offset: number; length: number }[] = [];
    const matmulOutputs: WebGLTensor[] = [];
    // split by outShape0 -> im2col -> matmul -> concat
    const rectangleCase = group * batch * defaultChunkSize * outShape[1] < context.maxTextureSize;
    for (let chunk = 0; chunk < chunkCount; chunk++) {
      const chunkOffset = chunk * defaultChunkSize;
      const chunkSize = Math.min(defaultChunkSize, outShape[0] - chunkOffset);
      chunkInfos.push({ offset: chunkOffset, length: chunkSize });
      const chunkGBout = group * batch * chunkSize * outShape[1];
      // W is reshaped to *, cinkhkw by optimizer
      if (rectangleCase) {
        if (context.webgl2 && cinkhkw % 4 === 0 && inputW.dimPerPixel === 4) {
          if (chOutPerGroup % 4 === 0) {
            // all 4ch

            const im2colData = context.emptyTensor(
              [
                group *
                  batch *
                  chunkSize *
                  outShape[1] *
                  chInPerGroup *
                  kernelShape[0] *
                  kernelShape[1],
              ],
              "float32",
              {
                dimPerPixel: 4,
                textureShape: [chunkGBout, cinkhkw / 4],
              }
            );
            await this.im2col4(
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
              chunkOffset,
              chunkSize
            );
            const matmulChunkData = context.emptyTensor(
              [chunkGBout * chOutPerGroup],
              "float32",
              {
                dimPerPixel: 4,
                textureShape: [chunkGBout, chOutPerGroup / 4],
              }
            );
            await this.matmul44(
              context,
              im2colData,
              inputW,
              matmulChunkData,
              group,
              batch * chunkSize * outShape[1],
              chInPerGroup * kernelShape[0] * kernelShape[1],
              chOutPerGroup
            );
            im2colData.dispose();
            matmulOutputs.push(matmulChunkData);
          } else {
            // input 4ch, output 1ch

            const im2colData = context.emptyTensor(
              [
                group *
                  batch *
                  chunkSize *
                  outShape[1] *
                  chInPerGroup *
                  kernelShape[0] *
                  kernelShape[1],
              ],
              "float32",
              {
                dimPerPixel: 4,
                textureShape: [chunkGBout, cinkhkw / 4],
              }
            );
            await this.im2col4(
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
              chunkOffset,
              chunkSize
            );
            const matmulChunkData = context.emptyTensor(
              [chunkGBout * chOutPerGroup],
              "float32",
              {
                dimPerPixel: 1,
                textureShape: [chunkGBout, chOutPerGroup],
              }
            );
            await this.matmul41(
              context,
              im2colData,
              inputW,
              matmulChunkData,
              group,
              batch * chunkSize * outShape[1],
              chInPerGroup * kernelShape[0] * kernelShape[1],
              chOutPerGroup
            );
            im2colData.dispose();
            matmulOutputs.push(matmulChunkData);
          }
        } else {
          // all 1ch

          const im2colData = context.emptyTensor(
            [
              group *
                batch *
                chunkSize *
                outShape[1] *
                chInPerGroup *
                kernelShape[0] *
                kernelShape[1],
            ],
            "float32",
            {
              dimPerPixel: 1,
              textureShape: [
                group * batch * chunkSize * outShape[1],
                chInPerGroup * kernelShape[0] * kernelShape[1],
              ],
            }
          );
          await this.im2col1(
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
            chOutPerGroup,
            chunkOffset,
            chunkSize
          );
          const matmulChunkData = context.emptyTensor(
            [group * batch * chunkSize * outShape[1] * chOutPerGroup],
            "float32",
            {
              dimPerPixel: 1,
              textureShape: [
                group * batch * chunkSize * outShape[1],
                chOutPerGroup,
              ],
            }
          );
          await this.matmul11(
            context,
            im2colData,
            inputW,
            matmulChunkData,
            group,
            batch * chunkSize * outShape[1],
            chInPerGroup * kernelShape[0] * kernelShape[1],
            chOutPerGroup
          );
          im2colData.dispose();
          matmulOutputs.push(matmulChunkData);
        }
      } else {
        if (inputW.dimPerPixel === 4) {
          // generic but W is 4ch

          const im2colData = context.emptyTensor([
            group *
              batch *
              chunkSize *
              outShape[1] *
              chInPerGroup *
              kernelShape[0] *
              kernelShape[1],
          ]);
          await this.im2col1(
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
            chOutPerGroup,
            chunkOffset,
            chunkSize
          );
          const matmulChunkData = context.emptyTensor([
            group * batch * chunkSize * outShape[1] * chOutPerGroup,
          ]);
          await this.matmulgw4(
            context,
            im2colData,
            inputW,
            matmulChunkData,
            group,
            batch * chunkSize * outShape[1],
            chInPerGroup * kernelShape[0] * kernelShape[1],
            chOutPerGroup
          );
          im2colData.dispose();
          matmulOutputs.push(matmulChunkData);
        } else {
          // generic all 1ch

          const im2colData = context.emptyTensor([
            group *
              batch *
              chunkSize *
              outShape[1] *
              chInPerGroup *
              kernelShape[0] *
              kernelShape[1],
          ]);
          await this.im2col1(
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
            chOutPerGroup,
            chunkOffset,
            chunkSize
          );
          const matmulChunkData = context.emptyTensor([
            group * batch * chunkSize * outShape[1] * chOutPerGroup,
          ]);
          await this.matmulg1(
            context,
            im2colData,
            inputW,
            matmulChunkData,
            group,
            batch * chunkSize * outShape[1],
            chInPerGroup * kernelShape[0] * kernelShape[1],
            chOutPerGroup
          );
          im2colData.dispose();
          matmulOutputs.push(matmulChunkData);
        }
      }
    }
    if (matmulOutputs.length === 1) {
      matmulData = matmulOutputs[0];
    } else {
      matmulData = context.emptyTensor(
        [group * batch * outShape[0] * outShape[1] * chOutPerGroup],
        "float32",
        {
          dimPerPixel: matmulOutputs[0].dimPerPixel,
        }
      );
      await this.concat(
        context,
        matmulOutputs,
        matmulData,
        group * batch,
        outShape[0],
        outShape[1] * chOutPerGroup,
        chunkInfos
      );
      matmulOutputs.forEach((mO) => mO.dispose());
    }

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

      if (matmulData.dimPerPixel === 4) {
        await this.transpose4(
          context,
          matmulData,
          transposeData,
          group,
          batch,
          outShape[0] * outShape[1],
          chOutPerGroup
        );
      } else {
        await this.transpose1(
          context,
          matmulData,
          transposeData,
          group,
          batch,
          outShape[0] * outShape[1],
          chOutPerGroup
        );
      }
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
      if (matmulData.dimPerPixel === 4) {
        await this.transpose4(
          context,
          matmulData,
          output,
          group,
          batch,
          outShape[0] * outShape[1],
          chOutPerGroup
        );
      } else {
        await this.transpose1(
          context,
          matmulData,
          output,
          group,
          batch,
          outShape[0] * outShape[1],
          chOutPerGroup
        );
      }
      matmulData.dispose();
    }
    return [output];
  }

  private async transpose1(
    context: WebDNNWebGLContext,
    dT: WebGLTensor,
    dO: WebGLTensor,
    group: number,
    batch: number,
    outarea: number,
    chOutPerGroup: number
  ) {
    // DT(group, batch, outh, outw, choutpergroup) -> dO(batch, group, choutpergroup, outh, outw)

    const kernelName = `convreshapewebgl_transpose1`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  uniform int GROUP;
  uniform int BATCH;
  uniform int COPG;
  uniform int OUTAREA;
  
  ${shaderGenTensorNDGet("tex_input", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / OUTAREA;
    int x = rem - quo * OUTAREA;
    rem = quo;
    quo = rem / COPG;
    int c = rem - quo * COPG;
    rem = quo;
    quo = rem / GROUP;
    int g = rem - quo * GROUP;
    int b = quo;
  
    float s = 0.0;
    s = get_tex_input(((g * BATCH + b) * OUTAREA + x) * COPG + c);
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem("tex_input", [1], dT, context.webgl2),
      ...shaderGenTensorOutputUniformItem([dO.length], dO, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BATCH", type: "int", value: batch },
      { name: "COPG", type: "int", value: chOutPerGroup },
      { name: "OUTAREA", type: "int", value: outarea },
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dT, name: "tex_input" }],
      dO,
      uniforms
    );
  }

  private async concat(
    context: WebDNNWebGLContext,
    dCs: WebGLTensor[],
    dO: WebGLTensor,
    outerLength: number,
    concatLength: number,
    innerLength: number,
    chunks: { offset: number; length: number }[]
  ): Promise<void> {
    const dPP4 = dCs.every((dC) => dC.dimPerPixel === 4);
    if (!dPP4 && !dCs.every((dC) => dC.dimPerPixel === 1)) {
      throw new Error(
        "ConvReshapeWebGL: concat tensor's dimPerPixel is not unified"
      );
    }
    const kernelName = `convreshapewebgl_concat_${chunks.length}_${dPP4}`;
    if (!context.hasKernel(kernelName)) {
      const getEach = arange(chunks.length)
        .map((i) =>
          dPP4
            ? shaderGenTensorNDGetVec4(`tex_input_${i}`, 3, context.webgl2)
            : shaderGenTensorNDGet(`tex_input_${i}`, 3, context.webgl2)
        )
        .join("");
      const uniformChunks = arange(chunks.length)
        .map((i) => `uniform int CHUNK_OFS${i};`)
        .join("");
      let takeCode = `
if (tex_output_1 < CHUNK_OFS1) {
  s = get${
    dPP4 ? "_vec4" : ""
  }_tex_input_0(tex_output_0, tex_output_1, tex_output_2);
}
`;
      for (let i = 1; i < chunks.length - 1; i++) {
        takeCode += ` else if (tex_output_1 < CHUNK_OFS${i + 1}) {
  s = get${
    dPP4 ? "_vec4" : ""
  }_tex_input_${i}(tex_output_0, tex_output_1 - CHUNK_OFS${i}, tex_output_2);
}
`;
      }
      takeCode += `
else {
  s = get${dPP4 ? "_vec4" : ""}_tex_input_${
        chunks.length - 1
      }(tex_output_0, tex_output_1 - CHUNK_OFS${
        chunks.length - 1
      }, tex_output_2);
}
`;

      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(3)}
  ${uniformChunks}
  
  ${getEach}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(3)}
    ${dPP4 ? "vec4 s = vec4(0.0, 0.0, 0.0, 0.0);" : "float s = 0.0;"}

    ${takeCode}
    ${
      dPP4
        ? shaderGenOutputVec4("s", context.webgl2)
        : shaderGenOutput("s", context.webgl2)
    }
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const innerLengthPixel = dPP4 ? innerLength / 4 : innerLength;
    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorOutputUniformItem(
        [outerLength, concatLength, innerLengthPixel],
        dO,
        context.webgl2
      ),
    ];
    for (let i = 0; i < chunks.length; i++) {
      uniforms.push(
        ...shaderGenTensorNDGetUniformItem(
          `tex_input_${i}`,
          [chunks[i].length * innerLengthPixel, innerLengthPixel, 1],
          dCs[i],
          context.webgl2
        )
      );
      uniforms.push({
        name: `CHUNK_OFS${i}`,
        value: chunks[i].offset,
        type: "int",
      });
    }
    await context.runKernel(
      kernelName,
      dCs.map((dC, i) => ({ tensor: dC, name: `tex_input_${i}` })),
      dO,
      uniforms
    );
  }

  private async transpose4(
    context: WebDNNWebGLContext,
    dT: WebGLTensor,
    dO: WebGLTensor,
    group: number,
    batch: number,
    outarea: number,
    chOutPerGroup: number
  ) {
    // DT(group, batch, outh, outw, choutpergroup) -> dO(batch, group, choutpergroup, outh, outw)

    const kernelName = `convreshapewebgl_transpose4`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
    
    ${shaderGenTensorOutputUniform(1)}
    uniform int GROUP;
    uniform int BATCH;
    uniform int COPG;
    uniform int OUTAREA;
    
    ${shaderGenTensorNDGetVec4("tex_input", 1, context.webgl2)}
    
    void main() {
      ${shaderGenTensorOutputCoordsWithReturn(1)}
      int rem = tex_output_flat;
      int quo = rem / OUTAREA;
      int x = rem - quo * OUTAREA;
      rem = quo;
      quo = rem / COPG;
      int c = rem - quo * COPG;
      rem = quo;
      quo = rem / GROUP;
      int g = rem - quo * GROUP;
      int b = quo;

      int flat_index = ((g * BATCH + b) * OUTAREA + x) * COPG + c;
      int rgba_index = flat_index / 4;
      int color = flat_index - rgba_index * 4;
    
      float s = 0.0;
      switch (color) {
        case 0:
          s = get_vec4_tex_input(rgba_index).r;
          break;
        case 1:
          s = get_vec4_tex_input(rgba_index).g;
          break;
        case 2:
          s = get_vec4_tex_input(rgba_index).b;
          break;
        case 3:
          s = get_vec4_tex_input(rgba_index).a;
          break;
      }
      ${shaderGenOutput("s", context.webgl2)}
      return;
    }
    `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem("tex_input", [1], dT, context.webgl2),
      ...shaderGenTensorOutputUniformItem([dO.length], dO, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BATCH", type: "int", value: batch },
      { name: "COPG", type: "int", value: chOutPerGroup },
      { name: "OUTAREA", type: "int", value: outarea },
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dT, name: "tex_input" }],
      dO,
      uniforms
    );
  }
  private async bias(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dB: WebGLTensor,
    dO: WebGLTensor,
    batch: number,
    chOut: number,
    outarea: number
  ) {
    const kernelName = `convreshapewebgl_bias`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  uniform int BATCH;
  uniform int COUT;
  uniform int OUTAREA;
  
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_b", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / OUTAREA;
    int x = rem - quo * OUTAREA;
    rem = quo;
    quo = rem / COUT;
    int c = rem - quo * COUT;
    int b = quo;
  
    float s = 0.0;
    s = get_tex_input_i(tex_output_flat) + get_tex_input_b(c);
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dI,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_b",
        [1],
        dB,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dO.length], dO, context.webgl2),
      { name: "BATCH", type: "int", value: batch },
      { name: "COUT", type: "int", value: chOut },
      { name: "OUTAREA", type: "int", value: outarea },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dI, name: "tex_input_i" },
        { tensor: dB, name: "tex_input_b" },
      ],
      dO,
      uniforms
    );
  }

  private async im2col4(
    context: WebDNNWebGLContext,
    dX: WebGLTensor,
    dI: WebGLTensor,
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
    outShape0Offset: number,
    outShape0ChunkSize: number
  ) {
    const kernelName = `convreshapewebgl_im2col4_split`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
    
    ${shaderGenTensorOutputUniform(1)}
    uniform int GROUP;
    uniform int BATCH;
    uniform int O0;
    uniform int O1;
    uniform int CI;
    uniform int CIPG;
    uniform int K0;
    uniform int K1;
    uniform int S0;
    uniform int S1;
    uniform int P0;
    uniform int P1;
    uniform int D0;
    uniform int D1;
    uniform int IS0;
    uniform int IS1;
    uniform int O0OFS;
    uniform int O0CHUNK;
    
    ${shaderGenTensorNDGet("tex_input", 1, context.webgl2)}
    
    float get_one_pixel(int tex_output_flat) {
      int rem = tex_output_flat;
      int quo = rem / K0;
      int k1 = rem - quo * K1;
      rem = quo;
      quo = rem / K0;
      int k0 = rem - quo * K0;
      rem = quo;
      quo = rem / CIPG;
      int ci = rem - quo * CIPG;
      rem = quo;
      quo = rem / O1;
      int o1 = rem - quo * O1;
      rem = quo;
      quo = rem / O0CHUNK;
      int o0 = rem - quo * O0CHUNK + O0OFS;
      rem = quo;
      quo = rem / BATCH;
      int b = rem - quo * BATCH;
      int g = quo;
    
      int in0 = o0 * S0 - P0 + k0 * D0;
      int in1 = o1 * S1 - P1 + k1 * D1;
      float s = 0.0;
      if (in0 >= 0 && in0 < IS0 && in1 >= 0 && in1 < IS1) {
        s = get_tex_input(((b * CI + g * CIPG + ci) * IS0 + in0) * IS1 + in1);
      }

      return s;
    }

    void main() {
      ${shaderGenTensorOutputCoordsWithReturn(1)}
      vec4 s = vec4(get_one_pixel(tex_output_flat * 4),
                    get_one_pixel(tex_output_flat * 4 + 1),
                    get_one_pixel(tex_output_flat * 4 + 2),
                    get_one_pixel(tex_output_flat * 4 + 3));
      ${shaderGenOutputVec4("s", context.webgl2)}
      return;
    }
    `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem("tex_input", [1], dX, context.webgl2),
      ...shaderGenTensorOutputUniformItem([dI.length / 4], dI, context.webgl2), // Div by RGBA
      { name: "GROUP", type: "int", value: group },
      { name: "BATCH", type: "int", value: batch },
      { name: "O0", type: "int", value: outShape[0] },
      { name: "O1", type: "int", value: outShape[1] },
      { name: "CI", type: "int", value: chIn },
      { name: "CIPG", type: "int", value: chInPerGroup },
      { name: "K0", type: "int", value: kernelShape[0] },
      { name: "K1", type: "int", value: kernelShape[1] },
      { name: "S0", type: "int", value: strides[0] },
      { name: "S1", type: "int", value: strides[1] },
      { name: "P0", type: "int", value: pads[0] },
      { name: "P1", type: "int", value: pads[1] },
      { name: "D0", type: "int", value: dilations[0] },
      { name: "D1", type: "int", value: dilations[1] },
      { name: "IS0", type: "int", value: inShape[0] },
      { name: "IS1", type: "int", value: inShape[1] },
      { name: "O0OFS", type: "int", value: outShape0Offset },
      { name: "O0CHUNK", type: "int", value: outShape0ChunkSize },
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dX, name: "tex_input" }],
      dI,
      uniforms
    );
  }

  private async matmul44(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dW: WebGLTensor,
    dT: WebGLTensor,
    group: number,
    bout: number,
    cinkhkw: number,
    chOutPerGroup: number
  ) {
    /*
     * DI(group, bout, cinkhkw) * dW(group, coutpergroup, cinkhkw) -> dT(group, bout, coutpergroup)
     * ループ回数は定数が必要
     */
    const kernelName = `convreshapewebgl_matmul44_${cinkhkw}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  #define cinkhkw ${cinkhkw}
  #define cinkhkwdiv4 ${cinkhkw / 4}
  uniform int GROUP;
  uniform int BOUT;
  uniform int COPG;
  
  ${shaderGenTensorNDGet("tex_input_w", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  
  void main() {
    highp float helper_gfcx = gl_FragCoord.x;
    highp float helper_gfcy = gl_FragCoord.y;
    int xdiv4 = int(helper_gfcx - 0.5);
    int gy = int(helper_gfcy - 0.5);
    int g = gy / BOUT;
    int y = gy - g * BOUT;
  
    vec4 packs = vec4(0.0, 0.0, 0.0, 0.0);
    int iofs = g * BOUT + y;
    int wofs0 = g * COPG + xdiv4 * 4;
    int wofs1 = wofs0 + 1;
    int wofs2 = wofs0 + 2;
    int wofs3 = wofs0 + 3;
    for (int ip = 0; ip < cinkhkwdiv4; ip++) {
      vec4 tfi = texelFetch(tex_input_i, ivec2(ip, iofs), 0);
      vec4 tfw0 = texelFetch(tex_input_w, ivec2(ip, wofs0), 0);
      vec4 tfw1 = texelFetch(tex_input_w, ivec2(ip, wofs1), 0);
      vec4 tfw2 = texelFetch(tex_input_w, ivec2(ip, wofs2), 0);
      vec4 tfw3 = texelFetch(tex_input_w, ivec2(ip, wofs3), 0);
      packs += vec4(dot(tfi, tfw0), dot(tfi, tfw1), dot(tfi, tfw2), dot(tfi, tfw3));
    }
    ${shaderGenOutputVec4("packs", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_w",
        [1],
        dW,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dI,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dT.length / 4], dT, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BOUT", type: "int", value: bout },
      { name: "COPG", type: "int", value: chOutPerGroup },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dW, name: "tex_input_w" },
        { tensor: dI, name: "tex_input_i" },
      ],
      dT,
      uniforms
    );
  }

  private async matmul41(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dW: WebGLTensor,
    dT: WebGLTensor,
    group: number,
    bout: number,
    cinkhkw: number,
    chOutPerGroup: number
  ) {
    /*
     * DI(group, bout, cinkhkw) * dW(group, coutpergroup, cinkhkw) -> dT(group, bout, coutpergroup)
     * ループ回数は定数が必要
     */
    const kernelName = `convreshapewebgl_matmul41_${cinkhkw}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  #define cinkhkw ${cinkhkw}
  #define cinkhkwdiv4 ${cinkhkw / 4}
  uniform int GROUP;
  uniform int BOUT;
  uniform int COPG;
  
  ${shaderGenTensorNDGet("tex_input_w", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  
  void main() {
    highp float helper_gfcx = gl_FragCoord.x;
    highp float helper_gfcy = gl_FragCoord.y;
    int x = int(helper_gfcx - 0.5);
    int gy = int(helper_gfcy - 0.5);
    int g = gy / BOUT;
    int y = gy - g * BOUT;
  
    float s = 0.0;
    int iofs = g * BOUT + y;
    int wofs = g * COPG + x;
    for (int ip = 0; ip < cinkhkwdiv4; ip++) {
      s += dot(texelFetch(tex_input_i, ivec2(ip, iofs), 0), texelFetch(tex_input_w, ivec2(ip, wofs), 0));
    }
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_w",
        [1],
        dW,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dI,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dT.length], dT, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BOUT", type: "int", value: bout },
      { name: "COPG", type: "int", value: chOutPerGroup },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dW, name: "tex_input_w" },
        { tensor: dI, name: "tex_input_i" },
      ],
      dT,
      uniforms
    );
  }

  private async im2col1(
    context: WebDNNWebGLContext,
    dX: WebGLTensor,
    dI: WebGLTensor,
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
    chOutPerGroup: number,
    outShape0Offset: number,
    outShape0ChunkSize: number
  ) {
    const kernelName = `convreshapewebgl_im2col1_split`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  uniform int GROUP;
  uniform int BATCH;
  uniform int O0;
  uniform int O1;
  uniform int CI;
  uniform int CIPG;
  uniform int K0;
  uniform int K1;
  uniform int S0;
  uniform int S1;
  uniform int P0;
  uniform int P1;
  uniform int D0;
  uniform int D1;
  uniform int IS0;
  uniform int IS1;
  uniform int O0OFS;
  uniform int O0CHUNK;
  
  ${shaderGenTensorNDGet("tex_input", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / K0;
    int k1 = rem - quo * K1;
    rem = quo;
    quo = rem / K0;
    int k0 = rem - quo * K0;
    rem = quo;
    quo = rem / CIPG;
    int ci = rem - quo * CIPG;
    rem = quo;
    quo = rem / O1;
    int o1 = rem - quo * O1;
    rem = quo;
    quo = rem / O0CHUNK;
    int o0 = rem - quo * O0CHUNK + O0OFS;
    rem = quo;
    quo = rem / BATCH;
    int b = rem - quo * BATCH;
    int g = quo;
  
    int in0 = o0 * S0 - P0 + k0 * D0;
    int in1 = o1 * S1 - P1 + k1 * D1;
    float s = 0.0;
    if (in0 >= 0 && in0 < IS0 && in1 >= 0 && in1 < IS1) {
      s = get_tex_input(((b * CI + g * CIPG + ci) * IS0 + in0) * IS1 + in1);
    }
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem("tex_input", [1], dX, context.webgl2),
      ...shaderGenTensorOutputUniformItem([dI.length], dI, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BATCH", type: "int", value: batch },
      { name: "O0", type: "int", value: outShape[0] },
      { name: "O1", type: "int", value: outShape[1] },
      { name: "CI", type: "int", value: chIn },
      { name: "CIPG", type: "int", value: chInPerGroup },
      { name: "K0", type: "int", value: kernelShape[0] },
      { name: "K1", type: "int", value: kernelShape[1] },
      { name: "S0", type: "int", value: strides[0] },
      { name: "S1", type: "int", value: strides[1] },
      { name: "P0", type: "int", value: pads[0] },
      { name: "P1", type: "int", value: pads[1] },
      { name: "D0", type: "int", value: dilations[0] },
      { name: "D1", type: "int", value: dilations[1] },
      { name: "IS0", type: "int", value: inShape[0] },
      { name: "IS1", type: "int", value: inShape[1] },
      { name: "O0OFS", type: "int", value: outShape0Offset },
      { name: "O0CHUNK", type: "int", value: outShape0ChunkSize },
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dX, name: "tex_input" }],
      dI,
      uniforms
    );
  }

  private async matmul11(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dW: WebGLTensor,
    dT: WebGLTensor,
    group: number,
    bout: number,
    cinkhkw: number,
    chOutPerGroup: number
  ) {
    /*
     * DI(group, bout, cinkhkw) * dW(group, coutpergroup, cinkhkw) -> dT(group, bout, coutpergroup)
     * ループ回数は定数が必要
     */
    const kernelName = `convreshapewebgl_matmul11_${cinkhkw}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  #define cinkhkw ${cinkhkw}
  uniform int GROUP;
  uniform int BOUT;
  uniform int COPG;
  
  ${shaderGenTensorNDGet("tex_input_w", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  
  void main() {
    highp float helper_gfcx = gl_FragCoord.x;
    highp float helper_gfcy = gl_FragCoord.y;
    int x = int(helper_gfcx - 0.5);
    int gy = int(helper_gfcy - 0.5);
    int g = gy / BOUT;
    int y = gy - g * BOUT;
  
    float s = 0.0;
    ${
      context.webgl2
        ? `
    int iofs = g * BOUT + y;
    int wofs = g * COPG + x;
`
        : `
    float iofs = (float(g * BOUT + y) + 0.5) / float(tex_input_i_texture_h);
    float wofs = (float(g * COPG + x) + 0.5) / float(tex_input_w_texture_h);
`
    }
    for (int ip = 0; ip < cinkhkw; ip++) {
      ${
        context.webgl2
          ? "s += texelFetch(tex_input_i, ivec2(ip, iofs), 0).r * texelFetch(tex_input_w, ivec2(ip, wofs), 0).r;"
          : "s += decode_float(texture2D(tex_input_i, vec2((float(ip) + 0.5) / float(tex_input_i_texture_w), iofs))) * decode_float(texture2D(tex_input_w, vec2((float(ip) + 0.5) / float(tex_input_w_texture_w), wofs)));"
      }
      
    }
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_w",
        [1],
        dW,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dI,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dT.length], dT, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BOUT", type: "int", value: bout },
      { name: "COPG", type: "int", value: chOutPerGroup },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dW, name: "tex_input_w" },
        { tensor: dI, name: "tex_input_i" },
      ],
      dT,
      uniforms
    );
  }

  private async matmulg1(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dW: WebGLTensor,
    dT: WebGLTensor,
    group: number,
    bout: number,
    cinkhkw: number,
    chOutPerGroup: number
  ) {
    /*
     * DI(group, bout, cinkhkw) * dW(group, coutpergroup, cinkhkw) -> dT(group, bout, coutpergroup)
     * ループ回数は定数が必要
     */
    const kernelName = `convreshapewebgl_matmulg1_${cinkhkw}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  #define cinkhkw ${cinkhkw}
  uniform int GROUP;
  uniform int BOUT;
  uniform int COPG;
  
  ${shaderGenTensorNDGet("tex_input_w", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / COPG;
    int x = rem - quo * COPG;
    rem = quo;
    quo = rem / BOUT;
    int y = rem - quo * BOUT;
    int g = quo;
  
    float s = 0.0;
    for (int ip = 0; ip < cinkhkw; ip++) {
      s += get_tex_input_i((g * BOUT + y) * cinkhkw + ip) * get_tex_input_w((g * COPG + x) * cinkhkw + ip);
    }
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_w",
        [1],
        dW,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dI,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dT.length], dT, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BOUT", type: "int", value: bout },
      { name: "COPG", type: "int", value: chOutPerGroup },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dW, name: "tex_input_w" },
        { tensor: dI, name: "tex_input_i" },
      ],
      dT,
      uniforms
    );
  }

  private async matmulgw4(
    context: WebDNNWebGLContext,
    dI: WebGLTensor,
    dW: WebGLTensor,
    dT: WebGLTensor,
    group: number,
    bout: number,
    cinkhkw: number,
    chOutPerGroup: number
  ) {
    /*
     * DI(group, bout, cinkhkw) * dW(group, coutpergroup, cinkhkw) -> dT(group, bout, coutpergroup)
     * ループ回数は定数が必要
     */
    const kernelName = `convreshapewebgl_matmulgw4_${cinkhkw}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  
  ${shaderGenTensorOutputUniform(1)}
  #define cinkhkw ${cinkhkw}
  #define cinkhkwdiv4 ${cinkhkw / 4}
  uniform int GROUP;
  uniform int BOUT;
  uniform int COPG;
  
  ${shaderGenTensorNDGetVec4("tex_input_w", 1, context.webgl2)}
  ${shaderGenTensorNDGet("tex_input_i", 1, context.webgl2)}
  
  void main() {
    ${shaderGenTensorOutputCoordsWithReturn(1)}
    int rem = tex_output_flat;
    int quo = rem / COPG;
    int x = rem - quo * COPG;
    rem = quo;
    quo = rem / BOUT;
    int y = rem - quo * BOUT;
    int g = quo;
  
    float s = 0.0;
    int iofs = (g * BOUT + y) * cinkhkw;
    int wofs = (g * COPG + x) * cinkhkwdiv4;
    for (int ip = 0; ip < cinkhkwdiv4; ip++) {
      s += dot(vec4(get_tex_input_i(iofs), get_tex_input_i(iofs+1), get_tex_input_i(iofs+2), get_tex_input_i(iofs+3)), get_vec4_tex_input_w(wofs));
      iofs += 4;
      wofs += 1;
    }
    ${shaderGenOutput("s", context.webgl2)}
    return;
  }
  `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_w",
        [1],
        dW,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_i",
        [1],
        dI,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem([dT.length], dT, context.webgl2),
      { name: "GROUP", type: "int", value: group },
      { name: "BOUT", type: "int", value: bout },
      { name: "COPG", type: "int", value: chOutPerGroup },
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dW, name: "tex_input_w" },
        { tensor: dI, name: "tex_input_i" },
      ],
      dT,
      uniforms
    );
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "ConvReshapeWebGL",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLConvReshapeWebGL(),
    },
  ];
}

"""

class PassConvReshapeWebGL(OptimizationPass):
    def __init__(self, webgl2: bool, max_texture_size: int) -> None:
        super().__init__()
        self.webgl2 = webgl2
        self.max_texture_size = max_texture_size

    def optimize(self, model: onnx.ModelProto) -> Optional[OptimizationPassResult]:
        graph = model.graph
        changed = False
        result = OptimizationPassResultWebGL()
        for node in graph.node:
            if node.op_type == "Conv":
                group = get_attr_int(node, "group", 1)
                weight_name = node.input[1]
                initializers = graph.initializer
                optimizable = False
                for initializer in initializers:
                    if initializer.name == weight_name:
                        weight_array = tensor_proto_to_numpy(initializer)
                        weight_array_shape = weight_array.shape
                        if len(weight_array_shape) != 4:
                            continue
                        cinpg_kh_kw = weight_array_shape[1] * weight_array_shape[2] * weight_array_shape[3]
                        cout = weight_array_shape[0]
                        if self.webgl2 and cinpg_kh_kw % 4 == 0:
                            if cinpg_kh_kw <= self.max_texture_size * 4 and cout <= self.max_texture_size:
                                optimizable = True
                        else:
                            if cinpg_kh_kw <= self.max_texture_size and cout <= self.max_texture_size:
                                optimizable = True
                if not optimizable:
                    continue
                changed = True
                # optimize it to ConvReshapeWebGL
                node.op_type = "ConvReshapeWebGL"
                # add hint to use RGBA texture for weight
                if self.webgl2 and cinpg_kh_kw % 4 == 0:
                    result.tensor_move_options[node.input[1]] = {"dimPerPixel": 4, "textureShape": [cout, cinpg_kh_kw // 4]}
                else:
                    result.tensor_move_options[node.input[1]] = {"dimPerPixel": 1, "textureShape": [cout, cinpg_kh_kw]}
                result.operator_shaders["convreshapewebgl"] = OperatorShaderWebGL(SHADER_CODE)
                # TODO: check weight is not used by other operator
        return result if changed else None
