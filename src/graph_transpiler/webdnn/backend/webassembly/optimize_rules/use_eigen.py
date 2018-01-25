from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.attribute import Attribute
from webdnn.graph.graph import Graph
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule

EIGEN_LICENSE = "(C) Eigen authors, MPL 2.0 License"


class UseEigenAttribute(Attribute):
    pass


class UseEigen(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Tensordot):
            if not op.has_attribute(UseEigenAttribute):
                op.attributes.add(UseEigenAttribute())
                flag_changed = True
                graph.licenses["eigen"] = EIGEN_LICENSE

        return graph, flag_changed
