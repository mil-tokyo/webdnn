from typing import Dict

from graph_builder.graph.operator import Operator
from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNCHW, OrderNHWC


class LocalResponseNormalization(Operator):
    """
    Local Response Normalization レイヤー
    CaffeNetを再現するために実装
    """
    attributes = {PostElementwise,
                  PostAxiswise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {n: int, k: int, alpha: float, beta: float}
        :param name: 
        :param parameters: 
        """
        assert "n" in parameters
        assert "k" in parameters
        assert "alpha" in parameters
        assert "beta" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        y = Variable(x.shape, x.axis_order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
