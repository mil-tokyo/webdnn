from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.attribute import Attribute
from webdnn.graph.graph import Graph
from webdnn.graph.operators.sgemm import Sgemm
from webdnn.graph.optimize_rule import OptimizeRule

EIGEN_LICENSE = "(C) Eigen authors, MPL 2.0 License"


class SgemmWithEigen(Attribute):
    pass


class OptimizeSgemmEigen(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Sgemm):  # type: Sgemm

            if not op.has_attribute(SgemmWithEigen):
                op.attributes.add(SgemmWithEigen(op))
                flag_changed = True
                graph.licenses["eigen"] = EIGEN_LICENSE

        return graph, flag_changed
