from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class MergeTensordotAndElementwiseMul(OptimizeRule):
    """
    This optimize rule merges Tensordot weight and ElementwiseMul coefficient.

    ... code-block:: text

         x -+
            +-{tensordot}- h -+
        w1 -+                 +-{mul}- y
                          w2 -+

    In above sub structure, if some conditions are satisfied, it can be simplified as follows,

    ... code-block::

              x -+
                 +-{tensordot}- y
        w1 * w2 -+
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.MERGE_TENSORDOT_AND_ELEMENTWISE_MUL,
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        matches = traverse.search_sub_structure(graph, [Tensordot, Variable, ElementwiseMul, Variable])
        while len(matches) > 0:
            tensordot, h, elementwise_mul, y = matches.pop()  # type: Tensordot, Variable, ElementwiseMul, Variable
            if len(h.input_to) != 1:
                # h will be removed by this optimization rule
                continue

            if isinstance(tensordot.inputs["A"], ConstantVariable):
                w1 = tensordot.inputs["A"]  # type: ConstantVariable
                reduced_axes = tensordot.axes[0]

            elif isinstance(tensordot.inputs["B"], ConstantVariable):
                w1 = tensordot.inputs["B"]  # type: ConstantVariable
                reduced_axes = tensordot.axes[1]

            else:
                continue

            if isinstance(elementwise_mul.inputs["x0"], ConstantVariable) and elementwise_mul.inputs["x1"] == h:
                w2 = elementwise_mul.inputs["x0"]  # type: ConstantVariable

            elif isinstance(elementwise_mul.inputs["x1"], ConstantVariable) and elementwise_mul.inputs["x0"] == h:
                w2 = elementwise_mul.inputs["x1"]  # type: ConstantVariable

            else:
                continue

            if any(axis not in w1.order.axes for axis in w2.order.axes):
                continue

            if any(axis in reduced_axes for axis in w2.order.axes):
                continue

            flag_changed = True
            elementwise_mul.remove_all()
            OptimizeRule.replace_variable(graph, w1, ConstantVariable(w1.data, w1.order) * w2, with_assert=False)
            OptimizeRule.replace_variable(graph, h, y, with_assert=False)

        return graph, flag_changed
