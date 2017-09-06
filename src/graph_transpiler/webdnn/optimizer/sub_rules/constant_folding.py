from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class ConstantFolding(OptimizeRule):
    """
    Calculate constant expression in compile time
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.CONSTANT_FOLDING
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        for op in traverse.listup_operators(graph):
            if op.fold_constance == Operator.fold_constance:
                continue

            if all(isinstance(v, ConstantVariable) for v in op.inputs.values()):
                op.fold_constance()
                flag_changed = True

        return graph, flag_changed