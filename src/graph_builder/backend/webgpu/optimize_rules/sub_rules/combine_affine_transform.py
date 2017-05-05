from typing import Tuple

from graph_builder.backend.webgpu.operators.affine_transform import AffineTransform
from graph_builder.graph.graph import Graph
from graph_builder.optimize_rule.optimize_rule import OptimizeRule
from graph_builder.optimize_rule.util import search_sub_structure
from graph_builder.util import flags


class CombineAffineTransform(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not flags.optimize.OPTIMIZE_AFFINE_TRANSFORM:
            return graph, False

        matches = search_sub_structure(graph, [AffineTransform, AffineTransform])
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
