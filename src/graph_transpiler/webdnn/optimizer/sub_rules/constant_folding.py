from typing import Tuple, Optional, Type

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

    def optimize(self, graph: Graph, target_ops: Optional[Tuple[Type[Operator]]] = None) -> Tuple[Graph, bool]:
        flag_changed = False

        for op in traverse.listup_operators(graph):
            if getattr(op.fold_constance, '__func__', None) is Operator.fold_constance:
                # fold_constance is not implemented
                continue

            if all(isinstance(v, ConstantVariable) for v in op.inputs.values()):
                if target_ops is not None and not isinstance(op, target_ops):
                    continue
                op.fold_constance(graph)
                flag_changed = True

        return graph, flag_changed
