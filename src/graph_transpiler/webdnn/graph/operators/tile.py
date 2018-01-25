from typing import Optional

import numpy as np

from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


class Tile(Operator):
    """Tile(name)
    Repeat input variable.

    Args:
        name (str): Operator name.
        multiplier (tuple of int): number of repeat

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable.

    """

    def __init__(self, name: Optional[str], multiplier: AxisKeyDict[int]):
        super().__init__(name)
        self.parameters["multiplier"] = multiplier

    def __call__(self, x: Variable):
        assert x.ndim == len(self.multiplier), f"""
[Tile] Number of multiplier must be same as # of dimension of x:
    (x.ndim)={x.ndim}
    (len(self.multiplier))={len(self.multiplier)}"""

        y_shape = [self.multiplier[a] * x.shape_dict[a] for a in x.order.axes]
        y = Variable(y_shape, x.order)

        self.append_input("x", x)
        self.append_output("y", y)
        return y,

    @property
    def multiplier(self) -> AxisKeyDict[int]:
        return self.parameters["multiplier"]

    def fold_constance(self, graph: Graph):
        x = self.inputs["x"]  # type: ConstantVariable
        y = self.outputs["y"]

        new_y = ConstantVariable(np.tile(x.data, [self.multiplier[a] for a in x.order.axes]), x.order)
        new_y.change_order(y.order)
        OptimizeRule.replace_variable(graph, y, new_y)
        self.remove_all()
