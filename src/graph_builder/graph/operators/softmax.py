from typing import Dict

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.variable import Variable


class Softmax(Operator):
    """
    Softmaxレイヤー
    """
    attributes = {Inplace}

    def __init__(self, name: str, parameters: Dict[str, object] = None):
        """
        :param name: 
        :param parameters: 
        """
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        y = Variable(x.shape, x.axis_order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
