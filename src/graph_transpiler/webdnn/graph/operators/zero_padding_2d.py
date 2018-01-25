from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


class ZeroPadding2D(Operator):
    """ZeroPadding2D(name, padding)

    Zero padding 2D operator

    Supposed to be merged into convolution in optimization

    Args:
        name (str): Operator name.
        padding (int or tuple of int): Padding size. [top, left]

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
        H2 = x_shape_dict[Axis.H] + 2 * self.parameters["padding"][0]
        W2 = x_shape_dict[Axis.W] + 2 * self.parameters["padding"][1]
        C2 = x_shape_dict[Axis.C]

        y = Variable([N, H2, W2, C2], OrderNHWC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

        self.append_input("x", x)
        self.append_output("y", y)
        return y,
