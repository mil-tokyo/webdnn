import numpy as np

from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.constant_variable import ConstantVariable


class Sqrt(Elementwise):
    """Sqrt(name)

    Square root operator.

    .. math::

        f(x) = sqrt(x)

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """

    def fold_constance(self, graph: Graph):
        x0 = self.inputs["x0"]  # type: ConstantVariable
        y = self.outputs["y"]

        new_y = ConstantVariable(np.sqrt(x0.data), x0.order)
        new_y.change_order(y.order)
        OptimizeRule.replace_variable(graph, y, new_y)
        self.remove_all()
