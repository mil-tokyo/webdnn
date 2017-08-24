from typing import Dict, Any

from webdnn.graph.variable import Variable
from webdnn.util import json


class KernelExecutionInfo(json.SerializableMixin):
    shader_name: str
    inputs: Dict[str, Variable]
    uniforms: Dict[str, Dict[str, Any]]
    output: Variable

    def __init__(self,
                 shader_name: str,
                 inputs: Dict[str, Variable],
                 uniforms: Dict[str, Dict[str, Any]],
                 output: Variable):
        self.shader_name = shader_name
        self.inputs = inputs
        self.uniforms = uniforms
        self.output = output

    def _to_serializable_(self):
        return {
            "shader_name": self.shader_name,
            "inputs": self.inputs,
            "uniforms": self.uniforms,
            "output": self.output.parameters["name"]
        }


class Kernel:
    source: str
    exec_info: KernelExecutionInfo

    def __init__(self,
                 source: str,
                 shader_name: str,
                 inputs: Dict[str, Variable],
                 uniforms: Dict[str, Dict[str, Any]],
                 output: Variable):
        self.source = source
        self.exec_info = KernelExecutionInfo(
            shader_name=shader_name,
            inputs=inputs,
            uniforms=uniforms,
            output=output
        )
