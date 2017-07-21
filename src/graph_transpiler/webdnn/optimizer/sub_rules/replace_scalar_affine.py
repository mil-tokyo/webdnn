from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.util import flags


class ReplaceScalarAffine(OptimizeRule):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REPLACE_SCALAR_AFFINE
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), ScalarAffine):  # type: ScalarAffine
            x = op.inputs["x0"]
            y = op.outputs["y"]
            op.remove_all()

            y_dummy = x * op.scale + op.bias  # type: Variable
            y_dummy.change_order(y.order)
            y_dummy.replace(y)

            flag_changed = True

        return graph, flag_changed
