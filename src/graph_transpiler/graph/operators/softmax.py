from typing import Optional

from graph_transpiler.graph.operator import Operator
from graph_transpiler.graph.operators.attributes.inplace import Inplace
from graph_transpiler.graph.variable import Variable


class Softmax(Operator):
    """Softmax operator 

    Args:
        name (str): Operator name.

    """
    def __init__(self, name: Optional[str]):
        super().__init__(name)
        self.attributes = {Inplace(self, "x", "y")}

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~graph_transpiler.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~graph_transpiler.graph.variable.Variable`: Output
        """
        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
