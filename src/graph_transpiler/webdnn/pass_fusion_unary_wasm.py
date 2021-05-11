from typing import List
import onnx
from webdnn.pass_fusion_unary import PassFusionUnary
from webdnn.operator_shader_wasm import OperatorShaderWasm
from webdnn.optimization_pass_result_wasm import OptimizationPassResultWasm

TS_TEMPLATE = """
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNWasmContext } from "../../../../interface/backend/wasm/wasmContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class WasmUnary extends OperatorImpl {
  constructor(private kernelName: string) {
    super("wasm");
  }

  async run(context: WebDNNWasmContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsWasmTensorArray(inputs);
    const input = inputs[0];
    if (input.dataType !== "float32") {
      throw new Error("Only float32 is supported");
    }
    const output = context.emptyTensor(input.dims, input.dataType);
    context.runKernel(this.kernelName, [
      { type: "tensor", value: input },
      { type: "tensor", value: output },
      { type: "int32", value: input.length },
    ]);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "%%OP_TYPE%%",
      backend: "wasm",
      opsetMin: 1,
      factory: () => new WasmUnary("%%OP_TYPE%%"),
    },
  ];
}
"""

CPP_TEMPLATE = """
#include <algorithm>
#include <cmath>
#include "../../common/kernel.hpp"
#include "../../common/unary.hpp"

extern "C"
{
  void WEBDNN_KERNEL %%OP_TYPE%%(const float *src, float *dst, int length)
  {
    webdnn_unary(src, dst, length, [](float v0) { %%FUNC_BODY%% });
  }
}
"""

FUNC_TEMPLATES = {
    "Ceil": "float %%VAR_OUT%% = std::ceil(%%VAR_IN%%);",
    "Exp": "float %%VAR_OUT%% = std::exp(%%VAR_IN%%);",
    "Floor": "float %%VAR_OUT%% = std::floor(%%VAR_IN%%);",
    "Relu": "float %%VAR_OUT%% = std::max(%%VAR_IN%%, 0.0f);",
    "Sigmoid": "float %%VAR_OUT%% = (std::tanh(%%VAR_IN%% * 0.5f) + 1.0f) * 0.5f;",
    "Sqrt": "float %%VAR_OUT%% = std::sqrt(%%VAR_IN%%);",
    "Tanh": "float %%VAR_OUT%% = std::tanh(%%VAR_IN%%);",
}

class PassFusionUnaryWasm(PassFusionUnary):
    def _make_shader(self, custom_op_type: str, nodes: List[onnx.NodeProto]) -> OperatorShaderWasm:
        func_body = ""
        for i, node in enumerate(nodes):
            tmpl = FUNC_TEMPLATES[node.op_type]
            func_body += tmpl.replace("%%VAR_IN%%", f"v{i}").replace("%%VAR_OUT%%", f"v{i+1}")
        func_body += f"return v{len(nodes)};"
        ts_code = TS_TEMPLATE.replace("%%OP_TYPE%%", custom_op_type)
        cpp_code = CPP_TEMPLATE.replace("%%OP_TYPE%%", custom_op_type).replace("%%FUNC_BODY%%", func_body)
        return OperatorShaderWasm(ts_code, custom_op_type, cpp_code)

    def _construct_result(self):
        return OptimizationPassResultWasm()
