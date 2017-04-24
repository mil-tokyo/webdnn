from typing import Tuple

from graph_builder.backend.webgpu.operators.affine_transform import AffineTransform
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.constant_bias import ConstantBias
from graph_builder.graph.operators.constant_scale import ConstantScale
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule
from graph_builder.optimizer.optimizer import Optimizer


class UpgradeConstantScaleToAffineTransform(OptimizeRule):
    def __call__(self, graph: Operator) -> Tuple[Operator, bool]:
        matches = util.search_sub_structure(graph, [ConstantScale])
        if len(matches) == 0:
            return graph, False

        for match in matches:
            match[0].replace(AffineTransform("affine", {
                "scale": match[0].parameters["value"],
                "bias": 0
            }))

        return graph, True


class UpgradeConstantBiasToAffineTransform(OptimizeRule):
    def __call__(self, graph: Operator) -> Tuple[Operator, bool]:
        matches = util.search_sub_structure(graph, [ConstantBias])
        if len(matches) == 0:
            return graph, False

        for match in matches:
            match[0].replace(AffineTransform("affine", {
                "scale": 1,
                "bias": match[0].parameters["value"]
            }))

        return graph, True


class CombineAffineTransform(OptimizeRule):
    def __call__(self, graph: Operator) -> Tuple[Operator, bool]:
        matches = util.search_sub_structure(graph, [AffineTransform, AffineTransform])
        if len(matches) == 0:
            return graph, False

        for match in matches:
            a1: AffineTransform = match[0]
            a2: AffineTransform = match[1]

            y1 = a1.outputs["y"]
            y2 = a2.outputs["y"]

            a1.scale = a1.scale * a2.scale
            a1.bias = a1.bias * a2.scale + a2.bias

            a2.remove_all()
            a1.replace_output(y1, y2)

        return graph, True


class OptimizeAffineTransform(Optimizer):
    def __init__(self):
        super(OptimizeAffineTransform, self).__init__()

        self.register(UpgradeConstantBiasToAffineTransform())
        self.register(UpgradeConstantScaleToAffineTransform())
        self.register(CombineAffineTransform())
