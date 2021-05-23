# Use RGBA channel in WebGL2

from typing import Dict, Iterable, List, Optional
import numpy as np
import onnx
from webdnn.optimization_pass_result_webgl import OptimizationPassResultWebGL
from webdnn.optimization_pass import OptimizationPass, OptimizationPassResult
from webdnn.onnx_util import tensor_proto_to_numpy, get_attr_int
from webdnn.operator_shader_webgl import OperatorShaderWebGL

SHADER_CODE = """import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { WebGLTensor } from "../../../../interface/backend/webgl/webglTensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { calcStrides } from "../../../operatorUtil";
import { OperatorImpl } from "../../../operatorImpl";

// Version 13
class MatMulNT141 extends OperatorImpl {
  constructor() {
    super("webgl");
  }

  protected calcShapeNT141(
    dimsA: ReadonlyArray<number>,
    dimsB: ReadonlyArray<number>
  ) {
    /*
     *Matmulの出力shape、入力stride計算
     *行列Bが転置状態かつ4chで入ってくる場合
     *matmul((a,b,m,k), (a,b,n,k)) => (a,b,m,n)
     *
     *a, bの部分は2個に限らず0~無限個の次元がつけられる。
     *2行列で各次元のサイズは一致が必要。
     *broadcastingあり。次元数が少ない側には先頭にサイズ1の次元が付与。
     *そのうえでサイズ1とそれ以外のサイズがある場合にそれ以外のサイズに合わせbroadcast
     *
     *一方の入力が１次元の場合の特例。
     *(k), (a,b,n,k) => (a,b,n)
     *(k)を(a,b,1,k)にbroadcastしたうえで計算して、(a,b,1,n)を得て、1の軸を消して(a,b,n)
     *
     *(a,b,m,k), (k) => (a,b,m)
     *(k)を(a,b,1,k)にbroadcastしたうえで計算して、(a,b,m,1)を得て、１の軸を消して(a,b,m)
     *
     *両方１次元だと、単純な内積で(1,1)を得て１の軸２つが消え、０次元のスカラー値。
     */

    // 出力の次元数（1次元の場合の特例適用前）
    const totalNDims = Math.max(dimsA.length, dimsB.length, 2),
      expandedDimsA = dimsA.slice();
    if (expandedDimsA.length === 0) {
      throw new Error();
    } else if (expandedDimsA.length === 1) {
      expandedDimsA.unshift(1);
    }
    while (expandedDimsA.length < totalNDims) {
      expandedDimsA.unshift(1);
    }
    const expandedDimsB = dimsB.slice();
    if (expandedDimsB.length === 0) {
      throw new Error();
    } else if (expandedDimsB.length === 1) {
      expandedDimsB.unshift(1);
    }
    while (expandedDimsB.length < totalNDims) {
      expandedDimsB.unshift(1);
    }

    const resultDims = [
        expandedDimsA[expandedDimsA.length - 2],
        expandedDimsB[expandedDimsB.length - 2],
      ],
      innerProductLength = expandedDimsA[expandedDimsA.length - 1];
    if (innerProductLength !== expandedDimsB[expandedDimsB.length - 1]) {
      throw new Error();
    }
    const stridesA = calcStrides(expandedDimsA),
      stridesB = calcStrides(expandedDimsB);
    for (let i = expandedDimsA.length - 3; i >= 0; i--) {
      const resultDim = Math.max(expandedDimsA[i], expandedDimsB[i]);
      // Broadcastされた次元はstrideは0 (出力サイズ1の次元でも0にしてOK)
      if (expandedDimsA[i] === 1) {
        stridesA[i] = 0;
      }
      if (expandedDimsB[i] === 1) {
        stridesB[i] = 0;
      }
      resultDims.unshift(resultDim);
    }
    // B is 4ch
    for (let i = 0; i < stridesB.length; i++) {
      stridesB[i] /= 4;
    }

    const resultDimsAfterSqueeze = resultDims.slice();
    if (dimsA.length === 1) {
      resultDimsAfterSqueeze.splice(resultDimsAfterSqueeze.length - 2, 1);
    }
    if (dimsB.length === 1) {
      resultDimsAfterSqueeze.splice(resultDimsAfterSqueeze.length - 1, 1);
    }

    return {
      resultDims,
      resultDimsAfterSqueeze,
      stridesA,
      stridesB,
      innerProductLength,
    };
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const inputA = inputs[0],
      inputB = inputs[1];
    if (!context.webgl2) {
      throw new Error("This operator can only run on WebGL2");
    }
    if (inputA.dataType !== "float32" || inputB.dataType !== "float32") {
      throw new Error("only float32 is supported");
    }
    if (inputA.dimPerPixel !== 1 || inputB.dimPerPixel !== 4) {
      throw new Error();
    }
    const {
        resultDims,
        resultDimsAfterSqueeze,
        stridesA,
        stridesB,
        innerProductLength,
      } = this.calcShapeNT141(inputA.dims, inputB.dims),
      output = context.emptyTensor(resultDimsAfterSqueeze, "float32", 1);
    console.dir(this.calcShapeNT141(inputA.dims, inputB.dims));
    if (resultDims.length === 2) {
      await this.calcDim2(
        context,
        inputA,
        inputB,
        output,
        resultDims,
        stridesA,
        stridesB,
        innerProductLength
      );
    } else if (resultDims.length === 3) {
      await this.calcDim3(
        context,
        inputA,
        inputB,
        output,
        resultDims,
        stridesA,
        stridesB,
        innerProductLength
      );
    } else {
      // TODO: 4次元以上のサポート
      throw new Error();
    }

    return [output];
  }

  private async calcDim2(
    context: WebDNNWebGLContext,
    dA: WebGLTensor,
    dB: WebGLTensor,
    dC: WebGLTensor,
    resultDims: number[],
    stridesA: ReadonlyArray<number>,
    stridesB: ReadonlyArray<number>,
    innerProductLength: number
  ) {
    const kernelSource = `${shaderGenHeader(context.webgl2)}

#define innerProductLengthDiv4 ${innerProductLength / 4}
${shaderGenTensorOutputUniform(resultDims.length)}

uniform sampler2D tex_input_a;
uniform int tex_input_a_stride_0;
uniform int tex_input_a_stride_1;

ivec2 get_coord_a(int d0) {
  int flat_index = d0 * tex_input_a_stride_0;
  int texture_w = textureSize(tex_input_a, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

uniform sampler2D tex_input_b;
uniform int tex_input_b_stride_0;
uniform int tex_input_b_stride_1;

ivec2 get_coord_b(int d0) {
  int flat_index = d0 * tex_input_b_stride_0;
  int texture_w = textureSize(tex_input_b, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(resultDims.length)}
  float s = 0.0;
  ivec2 c_a = get_coord_a(tex_output_0);
  ivec2 c_b = get_coord_b(tex_output_1);
  int texture_w_a = textureSize(tex_input_a, 0).x;
  int texture_w_b = textureSize(tex_input_b, 0).x;
  for (int ip = 0; ip < innerProductLengthDiv4; ip++) {
    vec4 vec_a;
    vec_a.r = texelFetch(tex_input_a, c_a, 0).r;
    c_a.x += 1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    vec_a.g = texelFetch(tex_input_a, c_a, 0).r;
    c_a.x += 1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    vec_a.b = texelFetch(tex_input_a, c_a, 0).r;
    c_a.x += 1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    vec_a.a = texelFetch(tex_input_a, c_a, 0).r;
    c_a.x += 1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    vec4 vec_b = texelFetch(tex_input_b, c_b, 0);
    s += dot(vec_a, vec_b);
    c_b.x += 1;
    if (c_b.x >= texture_w_b) {
      c_b = ivec2(c_b.x - texture_w_b, c_b.y + 1);
    }
  }
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`,
      kernelName = `matmulnt141_2_${innerProductLength}`;
    context.addKernel(kernelName, kernelSource);

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_a",
        stridesA,
        dA,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_b",
        stridesB,
        dB,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(resultDims, dC, context.webgl2),
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dA, name: "tex_input_a" },
        { tensor: dB, name: "tex_input_b" },
      ],
      dC,
      uniforms
    );
  }

  private async calcDim3(
    context: WebDNNWebGLContext,
    dA: WebGLTensor,
    dB: WebGLTensor,
    dC: WebGLTensor,
    resultDims: number[],
    stridesA: ReadonlyArray<number>,
    stridesB: ReadonlyArray<number>,
    innerProductLength: number
  ) {
    const kernelSource = `${shaderGenHeader(context.webgl2)}

#define innerProductLengthDiv4 ${innerProductLength / 4}
${shaderGenTensorOutputUniform(resultDims.length)}

uniform sampler2D tex_input_a;
uniform int tex_input_a_stride_0;
uniform int tex_input_a_stride_1;
uniform int tex_input_a_stride_2;

ivec2 get_coord_a(int d0, int d1) {
  int flat_index = d0 * tex_input_a_stride_0 + d1 * tex_input_a_stride_1;
  int texture_w = textureSize(tex_input_a, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

uniform sampler2D tex_input_b;
uniform int tex_input_b_stride_0;
uniform int tex_input_b_stride_1;
uniform int tex_input_b_stride_2;

ivec2 get_coord_b(int d0, int d1) {
  int flat_index = d0 * tex_input_b_stride_0 + d1 * tex_input_b_stride_1;
  int texture_w = textureSize(tex_input_b, 0).x;
  int y = flat_index / texture_w;
  int x = flat_index - y * texture_w;
  return ivec2(x, y);
}

void main() {
  ${shaderGenTensorOutputCoordsWithReturn(resultDims.length)}
  float s = 0.0;
  ivec2 c_a = get_coord_a(tex_output_0, tex_output_1);
  ivec2 c_b = get_coord_b(tex_output_0, tex_output_2);
  int texture_w_a = textureSize(tex_input_a, 0).x;
  int texture_w_b = textureSize(tex_input_b, 0).x;
  for (int ip = 0; ip < innerProductLengthDiv4; ip++) {
    vec4 vec_a;
    vec_a.r = texelFetch(tex_input_a, c_a, 0).r;
    c_a.x += 1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    vec_a.g = texelFetch(tex_input_a, c_a, 0).r;
    c_a.x += 1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    vec_a.b = texelFetch(tex_input_a, c_a, 0).r;
    c_a.x += 1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    vec_a.a = texelFetch(tex_input_a, c_a, 0).r;
    c_a.x += 1;
    if (c_a.x >= texture_w_a) {
      c_a = ivec2(c_a.x - texture_w_a, c_a.y + 1);
    }
    vec4 vec_b = texelFetch(tex_input_b, c_b, 0);
    s += dot(vec_a, vec_b);
    c_b.x += 1;
    if (c_b.x >= texture_w_b) {
      c_b = ivec2(c_b.x - texture_w_b, c_b.y + 1);
    }
  }
  ${shaderGenOutput("s", context.webgl2)}
  return;
}
`,
      kernelName = `matmulnt141_3_${innerProductLength}`;
    context.addKernel(kernelName, kernelSource);

    if (stridesA[2] > dA.textureWidth || stridesB[2] > dB.textureWidth) {
      throw new Error("MatMul: kernel assumption does not hold");
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_a",
        stridesA,
        dA,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_b",
        stridesB,
        dB,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(resultDims, dC, context.webgl2),
    ];
    await context.runKernel(
      kernelName,
      [
        { tensor: dA, name: "tex_input_a" },
        { tensor: dB, name: "tex_input_b" },
      ],
      dC,
      uniforms
    );
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "MatMulNT141",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new MatMulNT141(),
    },
  ];
}

"""

class PassMatMulTransposeWebGL2(OptimizationPass):
    def optimize(self, model: onnx.ModelProto) -> Optional[OptimizationPassResult]:
        graph = model.graph
        changed = False
        result = OptimizationPassResultWebGL()
        for node in graph.node:
            if node.op_type == "MatMul":
                rhs_name = node.input[1]
                initializers = graph.initializer
                optimizable = False
                rhs_array = None
                rhs_initializer = None
                for initializer in initializers:
                    if initializer.name == rhs_name:
                        rhs_array = tensor_proto_to_numpy(initializer)
                        rhs_array_shape = rhs_array.shape
                        if len(rhs_array_shape) < 2 or rhs_array_shape[-2] % 4 != 0:
                            continue
                        optimizable = True
                        rhs_initializer = initializer
                        break
                if not optimizable:
                    continue
                initializers.remove(rhs_initializer)
                changed = True
                # optimize it to MatMulNT141
                node.op_type = "MatMulNT141"
                # add hint to use RGBA texture for weight
                result.tensor_move_options[rhs_name] = {"dimPerPixel": 4}
                # move inner-product axis to last
                transposed_rhs_array = np.moveaxis(rhs_array, -2, -1)
                result.initializers[rhs_name] = transposed_rhs_array
                result.operator_shaders["matmulnt141"] = OperatorShaderWebGL(SHADER_CODE)
                # TODO: check weight is not used by other operator
        return result if changed else None
