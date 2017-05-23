from typing import Tuple

from webdnn.backend.webassembly.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.optimize_rule import OptimizeRule


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
