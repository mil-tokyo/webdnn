import numpy as np

from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.constant_variable import ConstantVariable


class Log(Elementwise):
    """Log(name)

    Logarithm operator.

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
        self.remove_all()

        y_new = ConstantVariable(x0.data, x0.order).change_order(y.order)
        y_new.data = np.log(y_new.data)
        OptimizeRule.replace_variable(graph, y, y_new)
