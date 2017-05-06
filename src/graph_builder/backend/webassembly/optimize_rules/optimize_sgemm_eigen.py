from typing import Tuple

from graph_builder.backend.webassembly.operators.sgemm import Sgemm
from graph_builder.graph import traverse
from graph_builder.graph.graph import Graph
from graph_builder.graph.optimize_rule import OptimizeRule


class OptimizeSgemmEigen(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.listup_operators(graph):
            if not isinstance(op, Sgemm):
                continue

            op: Sgemm

            if not op.parameters.get("eigen", False):
                op.parameters["eigen"] = True
                flag_changed = True

        return graph, flag_changed
