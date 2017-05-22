from typing import Tuple

from graph_transpiler.graph import traverse
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.operators.flatten import Flatten
from graph_transpiler.graph.optimize_rule import OptimizeRule
from graph_transpiler.util import flags


class RemoveUnnecessaryFlatten(OptimizeRule):
    """
    remove unnecessary flatten
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not flags.optimize.OPTIMIZE_INPLACE_OPERATION:
            return graph, False

        flag_changed = False
        for flatten in traverse.filter_nodes(traverse.listup_operators(graph), Flatten):  # type: Flatten
            x = flatten.inputs["x"]
            y = flatten.outputs["y"]

        return graph, flag_changed
