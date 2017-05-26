from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util import flags


class RemoveUnnecessaryFlatten(OptimizeRule):
    """
    remove unnecessary flatten
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not (flags.optimize.OPTIMIZE and flags.optimize.OPTIMIZE_INPLACE_OPERATION):
            return graph, False

        flag_changed = False
        for flatten in traverse.filter_nodes(traverse.listup_operators(graph), Flatten):  # type: Flatten
            x = flatten.inputs["x"]
            y = flatten.outputs["y"]

        return graph, flag_changed
