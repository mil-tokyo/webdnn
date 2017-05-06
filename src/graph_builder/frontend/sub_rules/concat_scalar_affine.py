from typing import Tuple

from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.scalar_affine import ScalarAffine
from graph_builder.graph.optimize_rule import OptimizeRule
from graph_builder.graph.traverse import search_sub_structure
from graph_builder.util import flags


class ConcatScalarAffine(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not flags.optimize.CONCAT_SCALAR_AFFINE:
            return graph, False

        flag_changed = False

        matches = search_sub_structure(graph, [ScalarAffine, ScalarAffine])
        while len(matches) > 0:
            match = matches[0]
            a1: ScalarAffine = match[0]
            a2: ScalarAffine = match[1]

            y1 = a1.outputs["y"]
            y2 = a2.outputs["y"]

            a1.scale = a1.scale * a2.scale
            a1.bias = a1.bias * a2.scale + a2.bias

            a2.remove_all()
            a1.replace_output(y1, y2)

            flag_changed = True
            matches = search_sub_structure(graph, [ScalarAffine, ScalarAffine])

        return graph, flag_changed
