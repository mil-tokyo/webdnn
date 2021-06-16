
from typing import List
import onnx
from webdnn.pass_fusion_unary_cpu import PassFusionUnaryCPU

from webdnn.optimization_pass import OptimizationPass, OptimizationPassResult
from webdnn.optimization_pass_result_cpu import OptimizationPassResultCPU
from webdnn.pass_fusion_unary_wasm import PassFusionUnaryWasm
from webdnn.optimization_pass_result_wasm import OptimizationPassResultWasm
from webdnn.pass_fusion_unary_webgl import PassFusionUnaryWebGL
from webdnn.pass_matmul_transpose_webgl2 import PassMatMulTransposeWebGL2
from webdnn.pass_conv_reshape_webgl import PassConvReshapeWebGL
from webdnn.optimization_pass_result_webgl import OptimizationPassResultWebGL

def make_backend_passes(backend: str) -> List[OptimizationPass]:
    if backend == "cpu":
        return [PassFusionUnaryCPU()]
    elif backend == "wasm":
        return [PassFusionUnaryWasm()]
    elif backend == "webgl1":
        return [PassFusionUnaryWebGL(), PassConvReshapeWebGL(webgl2=False)]
    elif backend == "webgl2":
        return [PassFusionUnaryWebGL(), PassConvReshapeWebGL(webgl2=True), PassMatMulTransposeWebGL2()]
    else:
        raise ValueError

def run_passes(model: onnx.ModelProto, backend: str) -> OptimizationPassResult:
    passes = make_backend_passes(backend)
    if backend == "cpu":
        result_merged = OptimizationPassResultCPU()
    elif backend == "wasm":
        result_merged = OptimizationPassResultWasm()
    elif backend.startswith("webgl"):
        result_merged = OptimizationPassResultWebGL()
    else:
        raise NotImplementedError
    for p in passes:
        result = p.optimize(model)
        if result is not None:
            result_merged.merge(result)
    return result_merged
