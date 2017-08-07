from typing import Optional

from webdnn.graph.operator import Operator
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


class ReinterpretAxis(Operator):
    """ReinterpretAxis(name, in_order, out_order)

    Re-interpret an axis as another semantics. Shape is not changed.

    In case of :code:`in_order` is :obj:`~webdnn.graph.order.OrderNC` and :code:`out_order` is :obj:`~webdnn.graph.order.OrderNT`,
    if :obj:`~webdnn.graph.order.OrderCN` variable is input, `~webdnn.graph.order.OrderTN` variable is output.

    Args:
        name (str): Operator name.
        in_order (:class:`~webdnn.Order`): Input order
        out_order (:class:`~webdnn.Order`): Output order

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable. Its shape is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], in_order: Order, out_order: Order):
        super().__init__(name)

        self.parameters["in_order"] = in_order
        self.parameters["out_order"] = out_order
        assert in_order.ndim == out_order.ndim, "ReinterpretAxis operator must not change variable's shape: " \
                                                f"in_order.ndim={in_order.ndim}, out_order.ndim={out_order.ndim}"

    def __call__(self, x: Variable):
        in_order = self.parameters["in_order"]  # type: Order
        out_order = self.parameters["out_order"]  # type: Order

        assert in_order.check_same_axes(x.order), "Shape mismatch: " \
                                                  f"op.in_order={self.parameters['in_order']}" \
                                                  f"x.order={x.order}"

        y = Variable(x.shape, Order([out_order.axes[in_order.axes_dict[axis]] for axis in x.order.axes]))
        self.append_input("x", x)
        self.append_output("y", y)

        return y,
