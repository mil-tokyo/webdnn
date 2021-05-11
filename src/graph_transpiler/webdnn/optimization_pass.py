from typing import Dict, Optional
import onnx

from webdnn.operator_shader import OperatorShader

class OptimizationPassResult:
    operator_shaders: Dict[str, OperatorShader]

    def __init__(self) -> None:
        self.operator_shaders = {}
    
    def merge(self, other: "OptimizationPassResult"):
        self.operator_shaders.update(other.operator_shaders)

    def write_code(self, root_directory: str):
        raise NotImplementedError

class OptimizationPass:
    def optimize(model: onnx.ModelProto) -> Optional[OptimizationPassResult]:
        raise NotImplementedError
