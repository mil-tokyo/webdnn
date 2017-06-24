from typing import Optional

from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.variable import Variable


class Softplus(Operator):
    """Softplus activation

    log(1 + exp(beta * x)) / beta

    Args:
        name (str): Operator name.
        beta (float): coefficient.

    """

    def __init__(self, name: Optional[str], beta: float):
        super().__init__(name)
        # in most case, beta == 1.0. Separating case of beta == 1.0 may improve performance.
        self.parameters["beta"] = float(beta)
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
