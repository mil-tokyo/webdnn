from typing import Optional, List, Union

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable


from webdnn.util.misc import mul


class ReinterpretAxis(Operator):
    """Re-interpret an axis as another semantics. Shape is not changed.

    Args:
        name (str): Operator name.

    """

    def __init__(self, name: Optional[str], in_order: Order, out_order: Order):

        super().__init__(name)

        self.parameters["in_order"] = in_order
        self.parameters["out_order"] = out_order
        assert in_order.ndim == out_order.ndim
        self.attributes = {}

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        assert self.parameters["in_order"] == x.order

        y = Variable(x.shape, self.parameters["out_order"])
        self.append_input("x", x)
        self.append_output("y", y)

        return y,
