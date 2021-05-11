import { OperatorImpl } from "../../../operatorImpl";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import { broadcastMulti } from "../../../operatorUtil";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";
import { OperatorEntry } from "../../../../interface/core/operator";

export class WebGLBinary7 extends OperatorImpl {
  constructor(
    public kernelName: string,
    private binaryCalculationSource: string
  ) {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const inputA = inputs[0];
    const inputB = inputs[1];
    if (inputA.dataType !== "float32" || inputB.dataType !== "float32") {
      throw new Error();
    }
    // elementwiseのアクセスにおいてテクスチャサイズが同じであることを仮定
    if (inputA.dimPerPixel !== 1 || inputB.dimPerPixel !== 1) {
      throw new Error();
    }

    const { dims: outShape, allStrides: inAllStrides } = broadcastMulti([
      inputA.dims,
      inputB.dims,
    ]);

    const outputTensor = context.emptyTensor(outShape, "float32");
    // gl_FragCoord.x: 0.5, 1.5, 2.5, ..., textureWidth-0.5
    // texture2D(textureName, vec2(x, y)): x=(0.5, 1.5, 2.5, ...) / textureWidth
    const outNdim = outShape.length;
    const kernelName = `${this.kernelName}_${outNdim}`;
    if (!context.hasKernel(kernelName)) {
      let idxs: string;
      switch (outNdim) {
        case 0:
          idxs = "";
          break;
        case 1:
          idxs = "tex_output_0";
          break;
        case 2:
          idxs = "tex_output_0, tex_output_1";
          break;
        case 3:
          idxs = "tex_output_0, tex_output_1, tex_output_2";
          break;
        case 4:
          idxs = "tex_output_0, tex_output_1, tex_output_2, tex_output_3";
          break;
        default:
          throw new Error();
      }
      const kernelSource = `${shaderGenHeader(context.webgl2)}
      
${shaderGenTensorOutputUniform(outNdim)}
${shaderGenTensorNDGet("tex_input_a", outNdim, context.webgl2)}
${shaderGenTensorNDGet("tex_input_b", outNdim, context.webgl2)}

    void main() {
      ${shaderGenTensorOutputCoordsWithReturn(outNdim)}
      float sa = get_tex_input_a(${idxs});
      float sb = get_tex_input_b(${idxs});
      ${this.binaryCalculationSource}
      ${shaderGenOutput("v", context.webgl2)}
      return;
    }
        `;
      context.addKernel(kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_a",
        inAllStrides[0],
        inputA,
        context.webgl2
      ),
      ...shaderGenTensorNDGetUniformItem(
        "tex_input_b",
        inAllStrides[1],
        inputB,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(
        outShape,
        outputTensor,
        context.webgl2
      ),
    ];

    await context.runKernel(
      kernelName,
      [
        { tensor: inputA, name: "tex_input_a" },
        { tensor: inputB, name: "tex_input_b" },
      ],
      outputTensor,
      uniforms
    );
    return [outputTensor];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    // Add, Sub, Mul, Div, Pow: opset under 7 requires explicit broadcast flag
    {
      opType: "Add",
      backend: "webgl",
      opsetMin: 7,
      factory: () => new WebGLBinary7("add", "float v = sa + sb;"),
    },
    {
      opType: "Sub",
      backend: "webgl",
      opsetMin: 7,
      factory: () => new WebGLBinary7("sub", "float v = sa - sb;"),
    },
    {
      opType: "Mul",
      backend: "webgl",
      opsetMin: 7,
      factory: () => new WebGLBinary7("mul", "float v = sa * sb;"),
    },
    {
      opType: "Div",
      backend: "webgl",
      opsetMin: 7,
      factory: () => new WebGLBinary7("div", "float v = sa / sb;"),
    },
    // pow(-1.1, 2) is error in GLSL, but useful in normalization algorithm
    {
      opType: "Pow",
      backend: "webgl",
      opsetMin: 7,
      factory: () => new WebGLBinary7("pow", "float v = pow(abs(sa), sb);"),
    },
  ];
}
