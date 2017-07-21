from typing import Tuple, List

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
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
        ops = traverse.listup_operators(graph)  # type: List[Operator]
        while len(ops) > 0:
            op1 = ops.pop()
            for x in op1.inputs.values():
                for op2 in list(x.input_to):
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

                    for y_name in list(op2.outputs.keys()):
                        v1 = op1.outputs[y_name]
                        v2 = op2.outputs[y_name]

                        op2.remove_output(v2)
                        v1.replace(v2)

                    op2.remove_all()
                    flag_changed = True
                    ops = traverse.listup_operators(graph)  # type: List[Operator]
                    break

        return graph, flag_changed
