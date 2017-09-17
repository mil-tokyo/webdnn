from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.commutative import Commutative
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class SimplifyCommutativeOperator(OptimizeRule):
    """
    Gather constant variable in commutative operator sequence in right hand
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_COMMUTATIVE_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Commutative):  # type: Operator
            attr = op.get_attribute(Commutative)[0]
            var1, var2 = attr.vars
            if not isinstance(var1, ConstantVariable):
                continue

            if isinstance(var2, ConstantVariable):
                continue

            attr.swap()
            flag_changed = True

        return graph, flag_changed
