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

export class ConvOptWebGL2 extends Conv {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    if (!context.webgl2) {
      throw new Error("This implementation only supports WebGL2");
    }
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
    if (
      inputX.dimPerPixel !== 1 ||
      inputW.dimPerPixel !== 4 ||
      (inputB && inputB.dimPerPixel !== 1)
    ) {
      throw new Error();
    }

    const im2colData = context.emptyTensor(
      [
        group *
          batch *
          outShape[0] *
          outShape[1] *
          chInPerGroup *
          kernelShape[0] *
          kernelShape[1],
      ],
      "float32",
      { dimPerPixel: 4 }
    );
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
      chInPerGroup
    );
    const matmulData = context.emptyTensor(
      [group * batch * outShape[0] * outShape[1] * chOutPerGroup],
      "float32",
      { dimPerPixel: 4 }
    );
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
    chInPerGroup: number
  ) {
    const kernelName = `convoptwebgl2_im2col`;
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
      quo = rem / O0;
      int o0 = rem - quo * O0;
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
    ];
    await context.runKernel(
      kernelName,
      [{ tensor: dX, name: "tex_input" }],
      dI,
      uniforms
    );
  }

  private async matmul(
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
    const kernelName = `convoptwebgl2_matmul_${cinkhkw}`;
    if (!context.hasKernel(kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
    
    ${shaderGenTensorOutputUniform(1)}
    #define cinkhkwdiv4 ${cinkhkw / 4}
    uniform int GROUP;
    uniform int BOUT;
    uniform int COPG;
    
    uniform sampler2D tex_input_w;
    uniform sampler2D tex_input_i;

    ivec2 first_idx_w(int flat_index) {
      int texture_w = textureSize(tex_input_w, 0).x;
      int y = flat_index / texture_w;
      int x = flat_index - y * texture_w;
      return ivec2(x, y);
    }

    ivec2 first_idx_i(int flat_index) {
      int texture_w = textureSize(tex_input_i, 0).x;
      int y = flat_index / texture_w;
      int x = flat_index - y * texture_w;
      return ivec2(x, y);
    }

    float calc_one_pixel(int tex_output_flat) {
      int rem = tex_output_flat;
      int quo = rem / COPG;
      int x = rem - quo * COPG;
      rem = quo;
      quo = rem / BOUT;
      int y = rem - quo * BOUT;
      int g = quo;
    
      float acc = 0.0;
      ivec2 c_i = first_idx_i((g * BOUT + y) * cinkhkwdiv4);
      ivec2 c_w = first_idx_w((g * COPG + x) * cinkhkwdiv4);
      int texture_w_i = textureSize(tex_input_i, 0).x;
      int texture_w_w = textureSize(tex_input_w, 0).x;
      for (int ip = 0; ip < cinkhkwdiv4; ip++) {
        acc += dot(texelFetch(tex_input_i, c_i, 0), texelFetch(tex_input_w, c_w, 0));
        c_i.x += 1;
        if (c_i.x >= texture_w_i) {
          c_i = ivec2(0, c_i.y + 1);
        }
        c_w.x += 1;
        if (c_w.x >= texture_w_w) {
          c_w = ivec2(0, c_w.y + 1);
        }
      }

      return acc;
    }

    void main() {
      ${shaderGenTensorOutputCoordsWithReturn(1)}
      vec4 s = vec4(calc_one_pixel(tex_output_flat * 4),
                    calc_one_pixel(tex_output_flat * 4 + 1),
                    calc_one_pixel(tex_output_flat * 4 + 2),
                    calc_one_pixel(tex_output_flat * 4 + 3));
      ${shaderGenOutputVec4("s", context.webgl2)}
      return;
    }
    `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorOutputUniformItem([dT.length / 4], dT, context.webgl2), // Div by RGBA
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

  private async transpose(
    context: WebDNNWebGLContext,
    dT: WebGLTensor,
    dO: WebGLTensor,
    group: number,
    batch: number,
    outarea: number,
    chOutPerGroup: number
  ) {
    // DT(group, batch, outh, outw, choutpergroup) -> dO(batch, group, choutpergroup, outh, outw)

    const kernelName = `convoptwebgl2_transpose`;
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
    const kernelName = `convoptwebgl2_bias`;
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
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "ConvOptWebGL2",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new ConvOptWebGL2(),
    },
  ];
}

"""

class PassConvPackWebGL2(OptimizationPass):
    def optimize(self, model: onnx.ModelProto) -> Optional[OptimizationPassResult]:
        graph = model.graph
        changed = False
        result = OptimizationPassResultWebGL()
        for node in graph.node:
            if node.op_type == "Conv":
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
                        if cinpg_kh_kw % 4 == 0 and weight_array_shape[0] % 4 == 0:
                            optimizable = True
                if not optimizable:
                    continue
                changed = True
                # optimize it to ConvOptWebGL2
                node.op_type = "ConvOptWebGL2"
                # add hint to use RGBA texture for weight
                result.tensor_move_options[node.input[1]] = {"dimPerPixel": 4}
                result.operator_shaders["convoptwebgl2"] = OperatorShaderWebGL(SHADER_CODE)
                # TODO: check weight is not used by other operator
        return result if changed else None
