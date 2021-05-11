from typing import List
import onnx
from webdnn.pass_fusion_unary import PassFusionUnary
from webdnn.operator_shader_cpu import OperatorShaderCPU
from webdnn.optimization_pass_result_webgl import OptimizationPassResultWebGL
from webdnn.operator_shader_webgl import OperatorShaderWebGL

SHADER_TEMPLATE = """
import { OperatorImpl } from "../../../operatorImpl";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import { Tensor } from "../../../../interface/core/tensor";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorElementwiseGet,
  shaderGenTensorElementwiseGetUniformItem,
} from "../../shaderHelper";
import { OperatorEntry } from "../../../../interface/core/operator";

export class WebGLUnary extends OperatorImpl {
  constructor(
    public kernelName: string,
    private unaryCalculationSource: string,
    private unaryCalculationSourceWebGL1?: string
  ) {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWebGLTensorArray(inputs);
    const input = inputs[0];
    if (input.dataType !== "float32") {
      throw new Error();
    }
    const outputTensor = context.emptyTensor(input.dims, "float32");
    if (
      input.textureWidth !== outputTensor.textureWidth ||
      input.textureHeight !== outputTensor.textureHeight ||
      input.dimPerPixel !== 1
    ) {
      throw new Error();
    }

    if (!context.hasKernel(this.kernelName)) {
      const kernelSource = `${shaderGenHeader(context.webgl2)}
  ${shaderGenTensorElementwiseGet("tex_input", context.webgl2)}
  void main() {
    float v0 = get_tex_input();
    ${
      !context.webgl2 && this.unaryCalculationSourceWebGL1
        ? this.unaryCalculationSourceWebGL1
        : this.unaryCalculationSource
    }
    ${shaderGenOutput("v", context.webgl2)}
    return;
  }
      `;
      context.addKernel(this.kernelName, kernelSource);
    }

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorElementwiseGetUniformItem(
        "tex_input",
        input,
        context.webgl2
      ),
    ];

    await context.runKernel(
      this.kernelName,
      [{ tensor: input, name: "tex_input" }],
      outputTensor,
      uniforms
    );
    return [outputTensor];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "%%OP_TYPE%%",
      backend: "webgl",
      opsetMin: 1,
      factory: () => new WebGLUnary("%%OP_TYPE%%", "%%FUNC_BODY_2%%", "%%FUNC_BODY_1%%"),
    },
  ];
}

"""

FUNC_TEMPLATES_2 = {
    "Ceil": "float %%VAR_OUT%% = ceil(%%VAR_IN%%);",
    "Exp": "float %%VAR_OUT%% = exp(%%VAR_IN%%);",
    "Floor": "float %%VAR_OUT%% = floor(%%VAR_IN%%);",
    "Relu": "float %%VAR_OUT%% = max(%%VAR_IN%%, 0.0);",
    "Sigmoid": "float %%VAR_OUT%% = (tanh(%%VAR_IN%% * 0.5) + 1.0) * 0.5;",
    "Sqrt": "float %%VAR_OUT%% = sqrt(%%VAR_IN%%);",
    "Tanh": "float %%VAR_OUT%% = tanh(%%VAR_IN%%);",
}

FUNC_TEMPLATES_1 = {
    "Ceil": "float %%VAR_OUT%% = ceil(%%VAR_IN%%);",
    "Exp": "float %%VAR_OUT%% = exp(%%VAR_IN%%);",
    "Floor": "float %%VAR_OUT%% = floor(%%VAR_IN%%);",
    "Relu": "float %%VAR_OUT%% = max(%%VAR_IN%%, 0.0);",
    "Sigmoid": "float %%VAR_OUT%% = 1.0 / (1.0 + exp(-%%VAR_IN%%));",
    "Sqrt": "float %%VAR_OUT%% = sqrt(%%VAR_IN%%);",
    "Tanh": "float %%VAR_OUT%%_t = exp(-2.0 * %%VAR_IN%%); float %%VAR_OUT%% = (1.0 - %%VAR_OUT%%_t) / (1.0 + %%VAR_OUT%%_t);",
}

class PassFusionUnaryWebGL(PassFusionUnary):
    def _make_shader(self, custom_op_type: str, nodes: List[onnx.NodeProto]) -> OperatorShaderCPU:
        func_body_1 = ""
        func_body_2 = ""
        for i, node in enumerate(nodes):
            tmpl = FUNC_TEMPLATES_1[node.op_type]
            func_body_1 += tmpl.replace("%%VAR_IN%%", f"v{i}").replace("%%VAR_OUT%%", f"v{i+1}")
            tmpl = FUNC_TEMPLATES_2[node.op_type]
            func_body_2 += tmpl.replace("%%VAR_IN%%", f"v{i}").replace("%%VAR_OUT%%", f"v{i+1}")
        func_body_1 += f"float v = v{len(nodes)};"
        func_body_2 += f"float v = v{len(nodes)};"
        ts_code = SHADER_TEMPLATE.replace("%%OP_TYPE%%", custom_op_type).replace("%%FUNC_BODY_1%%", func_body_1).replace("%%FUNC_BODY_2%%", func_body_2)
        return OperatorShaderWebGL(ts_code)

    def _construct_result(self):
        return OptimizationPassResultWebGL()
