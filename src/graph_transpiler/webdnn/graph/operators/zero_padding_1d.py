from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.axiswise import Axiswise
from webdnn.graph.operators.attributes.post_axiswise import PostAxiswise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNTC
from webdnn.graph.variable import Variable


class ZeroPadding1D(Operator):
    """Zero padding 1D operator

    Add padding to time-series data (n, t, c) -> (n, left + t + right, c)

    Args:
        name (str): Operator name.
        padding (int or tuple of int): Padding size. [left, right]
    """

    def __init__(self, name: Optional[str], padding: IntOrTuple):
        super().__init__(name)
        self.parameters["padding"] = to_tuple(padding)
        self.attributes = {PostAxiswise(self, Axis.C),
                           Axiswise(self, Axis.C)}

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        x_shape_dict = x.shape_dict
        N = x_shape_dict[Axis.N]
        T2 = x_shape_dict[Axis.T] + self.parameters["padding"][0] + self.parameters["padding"][1]
        C2 = x_shape_dict[Axis.C]

        y = Variable([N, T2, C2], OrderNTC)

        self.append_input("x", x)
        self.append_output("y", y)
        return y,
