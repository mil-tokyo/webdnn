import itertools
from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util import flags


class RemoveRedundantOperator(OptimizeRule):
    """
    This optimize rule merges operations they calculate same results.

    ... code-block:: text

                     w1 -+
                         +-{op3}
            +-{op1}- v1 -+
         x -+
            +-{op2}- v2 -+
                         +-{op4}
                     w2 -+

    If all parameters are same in both :code:`op1` and :code:`op2`, then it is simplified as follows

    ... code-block::

                   w1 -+
                       +-{op3}
         x -{op1}- v1 -+
                       +-{op4}
                   w2 -+
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.REMOVE_REDUNDANT_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        variables = traverse.listup_variables(graph)

        while len(variables) > 0:
            x = variables.pop()
            for op1, op2 in itertools.permutations(x.input_to, 2):
                if op2 is op1:
                    continue

                if op2.__class__ != op1.__class__:
                    # class is not same
                    continue

                if any((x_name not in op2.inputs) or (op2.inputs[x_name] != op1.inputs[x_name]) for x_name in op1.inputs.keys()):
                    # input is not same
                    continue

                if any((key not in op2.parameters) or (op2.parameters[key] != op1.parameters[key]) for key in op1.parameters.keys()):
                    # parameter is not same
                    continue

                flag_changed = True

                vs_1 = dict(op1.outputs)
                vs_2 = dict(op2.outputs)

                op2.remove_all()

                for v_name, v1 in vs_1.items():
                    v2 = vs_2[v_name]
                    if v1.order == v2.order:
                        """
                                    +-{op3}-
                        -{op1}- v1 -+
                                    +-{op4}-
                        """
                        OptimizeRule.replace_variable(graph, v2, v1)

                    else:
                        """
                                    +-{op3}-
                        -{op1}- v1 -+
                                    +-{Transpose}- v2 -{op4}-
                        """
                        v2_dummy, = Transpose(None)(v1)
                        v2_dummy.change_order(v2.order)
                        OptimizeRule.replace_variable(graph, v2_dummy, v2)

                variables = traverse.listup_variables(graph)
                break

        return graph, flag_changed
