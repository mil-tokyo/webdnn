from typing import Optional

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.variable import Variable


class Softmax(Operator):
    """Softmax operator 

    Args:
        name (str): Operator name.

    """
    attributes = {Inplace}

    def __init__(self, name: Optional[str]):
        super().__init__(name)

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~graph_builder.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
