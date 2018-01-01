from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNTC
from webdnn.graph.variable import Variable


class ZeroPadding1D(Operator):
    """ZeroPadding1D(name, padding)

    Zero padding 1D operator

    Add padding to time-series data (n, t, c) -> (n, left + t + right, c)

    Args:
        name (str): Operator name.
        padding (int or tuple of int): Padding size. [left, right]

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], padding: IntOrTuple):
        super().__init__(name)
        self.parameters["padding"] = to_tuple(padding)
        self.attributes.add(Tensorwise(Axis.C))
        self.attributes.add(Tensorwise(Axis.N))

    def __call__(self, x: Variable):
        x_shape_dict = x.shape_dict
        N = x_shape_dict[Axis.N]
        T2 = x_shape_dict[Axis.T] + self.parameters["padding"][0] + self.parameters["padding"][1]
        C2 = x_shape_dict[Axis.C]

        y = Variable([N, T2, C2], OrderNTC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

        self.append_input("x", x)
        self.append_output("y", y)
        return y,
