from typing import Optional

from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.variable import Variable


class LeakyRelu(Operator):
    """leaky relu activation

    max(x, slope*x)

    Args:
        name (str): Operator name.
        slope (float): slope in negative input.

    """

    def __init__(self, name: Optional[str], slope: float):
        super().__init__(name)
        self.parameters["slope"] = float(slope)
        self.attributes = {Elementwise(self),
                           Inplace(self, "x", "y")}

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
