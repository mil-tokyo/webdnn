from typing import Optional, List

from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


class Broadcast(Elementwise):
    """Broadcast(name, out_shape, out_order)

    Broadcast variable to specified shape.
    Each elementwise operator supports implicit broadcast feature. Therefore you don't need to use this operator explicitly.

    Args:
        name (str): Operator name.
        out_shape (list of int): target shape
        out_order (:obj:`~webdnn.Order`): target order

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable.
    """

    def __init__(self, name: Optional[str], out_shape: List[int], out_order: Order):
        super(Broadcast, self).__init__(name)
        self.parameters["out_shape"] = out_shape
        self.parameters["out_order"] = out_order

    def __call__(self, x: Variable):
        y = Variable(self.parameters["out_shape"], self.parameters["out_order"])
        self.append_input("x0", x)
        self.append_output("y", y)
        return y,
