from typing import Tuple

from graph_builder.backend.webgpu.operators.affine_transform import AffineTransform
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.constant_bias import ConstantBias
from graph_builder.optimize_rule.optimize_rule import OptimizeRule
from graph_builder.optimize_rule.util import search_sub_structure


class UpgradeConstantBiasToAffineTransform(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        matches = search_sub_structure(graph, [ConstantBias])
        if len(matches) == 0:
            return graph, False

        for match in matches:
            match[0].replace(AffineTransform("affine", {
                "scale": 1,
                "bias": match[0].parameters["value"]
            }))

        return graph, True
