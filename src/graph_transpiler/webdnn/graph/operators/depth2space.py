from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


class Depth2Space(Operator):
    """Depth2Space(name, r)

    Depth to space transformation.

    Args:
        name (str): Operator name.
        r (int): Upscaling factor.

    Signature
        .. code::

            y, = op(x, r)

        - **x** - Input variable.
        - **y** - Output variable. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], r: int):
        super().__init__(name)
        self.parameters["r"] = int(r)
        self.attributes.add(Tensorwise(Axis.N))

    def __call__(self, x: Variable):
        assert x.order.check_same_axes(OrderNHWC), "Input variable of Depth2Space must have N, C, H, and W axes.: " \
                                                   f"x.order.axes={x.order.axes}"
        assert x.shape_dict[Axis.C] % (self.parameters["r"] * self.parameters["r"]) == 0, \
            "Input variable C axis must be divisible by : " \
            f'r*r={self.parameters["r"]*self.parameters["r"]} ' \
            f"x.order.axes={x.order.axes}"

        N = x.shape_dict[Axis.N]
        C = x.shape_dict[Axis.C] // self.parameters["r"] // self.parameters["r"]
        H = x.shape_dict[Axis.H]
        W = x.shape_dict[Axis.W]
        y = Variable([N, H * self.parameters["r"], W * self.parameters["r"], C], OrderNHWC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

        self.append_input("x", x)
        self.append_output("y", y)
        return y,
