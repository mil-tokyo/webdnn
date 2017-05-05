from typing import Tuple

from graph_builder.backend.webassembly.operators.sgemm import Sgemm
from graph_builder.graph.graph import Graph
from graph_builder.optimize_rule import util
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class OptimizeSgemmEigen(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in util.listup_operators(graph):
            if not isinstance(op, Sgemm):
                continue

            op: Sgemm

            if not op.parameters["eigen"]:
                op.parameters["eigen"] = True
                flag_changed = True

        return graph, flag_changed
