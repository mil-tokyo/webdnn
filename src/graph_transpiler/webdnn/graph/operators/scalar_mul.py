from typing import Optional

from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.constant_variable import ConstantVariable


class ScalarMul(Elementwise):
    """ScalarMul(name, value)

    Elementwise multiply with scalar value

    Args:
        name (str): Operator name.
        value (int or float): the value

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.

        This operator also can be called by :code:`*`.

        .. code::

            y = x0 * value
    """

    def __init__(self, name: Optional[str], value: float):
        super().__init__(name)
        self.parameters["value"] = float(value)

    @property
    def value(self) -> float:
        return self.parameters["value"]

    def fold_constance(self, graph: Graph):
        x0 = self.inputs["x0"]  # type: ConstantVariable
        y = self.outputs["y"]  # type: ConstantVariable
        self.remove_all()

        y_new = ConstantVariable(x0.data, x0.order).change_order(y.order)
        y_new.data = y_new.data * self.value
        OptimizeRule.replace_variable(graph, y, y_new)
