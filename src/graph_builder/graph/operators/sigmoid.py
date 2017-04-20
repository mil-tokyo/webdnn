from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class Sigmoid(Operator):
    """
    Sigmoidレイヤー
    """
    attributes = {A.PostElementwise,
                  A.PostAxiswise,
                  A.Elementwise,
                  A.Channelwise,
                  A.Inplace}

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
        return y
