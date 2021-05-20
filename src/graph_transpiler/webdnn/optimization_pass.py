from typing import Dict, Optional
import onnx

from webdnn.operator_shader import OperatorShader

class OptimizationPassResult:
    operator_shaders: Dict[str, OperatorShader]
    tensor_move_options: Dict[str, dict]

    def __init__(self) -> None:
        self.operator_shaders = {}
        self.tensor_move_options = {}
    
    def merge(self, other: "OptimizationPassResult"):
        self.operator_shaders.update(other.operator_shaders)
        # TODO: check conflict for same tensor
        self.tensor_move_options.update(other.tensor_move_options)

    def write_code(self, root_directory: str):
        raise NotImplementedError

    def remove_code(self, root_directory: str):
        raise NotImplementedError

class OptimizationPass:
    def optimize(model: onnx.ModelProto) -> Optional[OptimizationPassResult]:
        raise NotImplementedError
