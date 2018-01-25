from typing import Optional

from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.constant_variable import ConstantVariable


class ScalarAffine(Elementwise):
    """ScalarAffine(name, value)

    Affine transform operator with scalar scale and value

    Args:
        name (str): Operator name.
        scale (int or float): the scale value
        bias (int or float): the bias value

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], scale: float, bias: float):
        super().__init__(name)
        self.scale = float(scale)
        self.bias = float(bias)

    @property
    def scale(self) -> float:
        return self.parameters["scale"]

    @scale.setter
    def scale(self, value: float):
        self.parameters["scale"] = value

    @property
    def bias(self) -> float:
        return self.parameters["bias"]

    @bias.setter
    def bias(self, value: float):
        self.parameters["bias"] = value

    def fold_constance(self, graph: Graph):
        x0 = self.inputs["x0"]  # type: ConstantVariable
        y = self.outputs["y"]  # type: ConstantVariable
        self.remove_all()

        y_new = ConstantVariable(x0.data, x0.order).change_order(y.order)
        y_new.data = y_new.data * self.scale + self.bias
        OptimizeRule.replace_variable(graph, y, y_new)
