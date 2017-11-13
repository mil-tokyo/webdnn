import numpy as np

from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.constant_variable import ConstantVariable


class Abs(Elementwise):
    """Abs(name)
    Elementwise absolute value operator.

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Absolute value of :code:`x`. Its shape and order is same as :code:`x0`.

        This operator also can be called by :func:`abs`.

        .. code::

            y = abs(x0)
    """

    def fold_constance(self, graph: Graph):
        x0 = self.inputs["x0"]  # type: ConstantVariable
        y = self.outputs["y"]
        self.remove_all()

        new_y = ConstantVariable(np.abs(x0.copy().change_order(y.order).data), y.order)
        OptimizeRule.replace_variable(graph, y, new_y)
