from typing import List
import onnx
from webdnn.pass_fusion_unary import PassFusionUnary
from webdnn.operator_shader_cpu import OperatorShaderCPU
from webdnn.optimization_pass_result_cpu import OptimizationPassResultCPU

SHADER_TEMPLATE = """
import { DataArrayConstructor, DataType } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class CPUUnary extends OperatorImpl {
  constructor(
    private op: (value: number) => number,
    private allowDataTypes: DataType[]
  ) {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    if (!this.allowDataTypes.includes(input.dataType)) {
      throw new Error(`Unary: DataType ${input.dataType} not supported`);
    }
    const newData = new DataArrayConstructor[input.dataType](input.data.length);
    const op = this.op;
    for (let i = 0; i < newData.length; i++) {
      newData[i] = op(input.data[i]);
    }
    const output = context.emptyTensor(input.dims, input.dataType, newData);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "%%OP_TYPE%%",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((v0) => {%%FUNC_BODY%%}, ["float32"]),
    },
  ];
}
"""

FUNC_TEMPLATES = {
    "Ceil": "const %%VAR_OUT%% = Math.ceil(%%VAR_IN%%);",
    "Exp": "const %%VAR_OUT%% = Math.exp(%%VAR_IN%%);",
    "Floor": "const %%VAR_OUT%% = Math.floor(%%VAR_IN%%);",
    "Relu": "const %%VAR_OUT%% = Math.max(%%VAR_IN%%, 0);",
    "Sigmoid": "const %%VAR_OUT%% = (Math.tanh(%%VAR_IN%% / 2) + 1) / 2;",
    "Sqrt": "const %%VAR_OUT%% = Math.sqrt(%%VAR_IN%%);",
    "Tanh": "const %%VAR_OUT%% = Math.tanh(%%VAR_IN%%);",
}

class PassFusionUnaryCPU(PassFusionUnary):
    def _make_shader(self, custom_op_type: str, nodes: List[onnx.NodeProto]) -> OperatorShaderCPU:
        func_body = ""
        for i, node in enumerate(nodes):
            tmpl = FUNC_TEMPLATES[node.op_type]
            func_body += tmpl.replace("%%VAR_IN%%", f"v{i}").replace("%%VAR_OUT%%", f"v{i+1}")
        func_body += f"return v{len(nodes)};"
        ts_code = SHADER_TEMPLATE.replace("%%OP_TYPE%%", custom_op_type).replace("%%FUNC_BODY%%", func_body)
        return OperatorShaderCPU(ts_code)

    def _construct_result(self):
        return OptimizationPassResultCPU()
