from typing import Tuple, List

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.operators.scalar_pow import ScalarPow
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util import flags


def remove_operator(op: Operator):
    x = op.inputs["x0"]
    y = op.outputs["y"]
    op.remove_all()
    x.replace(y)


class RemoveUnnecessaryOperator(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not (flags.optimize.OPTIMIZE and flags.optimize.CONCAT_SCALAR_OPERATION):
            return graph, False

        flag_changed = False

        nodes = traverse.listup_nodes(graph)

        filtered_nodes = traverse.filter_nodes(nodes, ScalarAffine)  # type: List[ScalarAffine]
        while len(filtered_nodes) > 0:
            op = filtered_nodes.pop()
            if op.scale == 1 and op.bias == 0:
                remove_operator(op)
                flag_changed = True

        filtered_nodes = traverse.filter_nodes(nodes, ScalarAdd)  # type: List[ScalarAdd]
        while len(filtered_nodes) > 0:
            op = filtered_nodes.pop()
            if op.value == 0:
                remove_operator(op)
                flag_changed = True

        filtered_nodes = traverse.filter_nodes(nodes, ScalarMul)  # type: List[ScalarMul]
        while len(filtered_nodes) > 0:
            op = filtered_nodes.pop()
            if op.value == 1:
                remove_operator(op)
                flag_changed = True

        filtered_nodes = traverse.filter_nodes(nodes, ScalarPow)  # type: List[ScalarPow]
        while len(filtered_nodes) > 0:
            op = filtered_nodes.pop()
            if op.value == 1:
                remove_operator(op)
                flag_changed = True

        return graph, flag_changed
