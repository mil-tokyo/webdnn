from typing import Optional, List

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


# FIXME: improve documentation
from webdnn.util.misc import mul


class Transpose(Operator):
    """Transposition. Doing nothing in frontend level,
    and do memory transposition in backend if input / output variable order differs.
    This layer is inserted in optimizer to support layers which accepts certain order.

    Args:
        name (str): Operator name.
    """

    def __init__(self, name: Optional[str]):

        super().__init__(name)

        self.attributes = {Elementwise(self)}

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        y = Variable(x.shape, x.order)
        self.append_input("x0", x)
        self.append_output("y", y)

        return y,
