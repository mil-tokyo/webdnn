from typing import Dict

from webdnn.graph.variable import Variable
from webdnn.util import json


class KernelExecutionInfo(json.SerializableMixin):
    shader_name: str
    inputs: Dict[str, Variable]
    output: Variable

    def __init__(self,
                 shader_name: str,
                 inputs: Dict[str, Variable],
                 output: Variable):
        self.shader_name = shader_name
        self.inputs = inputs
        self.output = output

    def _to_serializable_(self):
        return {
            "shader_name": self.shader_name,
            "uniforms": {},  # FIXME
            "inputs": {k: v.parameters["name"] for k, v in self.inputs.items()},
            "output": self.output.parameters["name"],
            "width": self.output.size
        }


class Kernel:
    source: str
    exec_info: KernelExecutionInfo

    def __init__(self,
                 source: str,
                 shader_name: str,
                 inputs: Dict[str, Variable],
                 output: Variable):
        self.source = source
        self.exec_info = KernelExecutionInfo(
            shader_name=shader_name,
            inputs=inputs,
            output=output
        )
