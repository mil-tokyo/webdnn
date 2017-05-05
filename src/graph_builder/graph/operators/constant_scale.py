from typing import Dict

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.axiswise import Axiswise
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


class ConstantScale(Operator):
    """
    全要素に定数スケールを乗算する
    """
    attributes = {PostElementwise,
                  PostAxiswise,
                  Axiswise,
                  Inplace,
                  HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {value: float}
        :param name: 
        :param parameters: 
        """
        assert "value" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        y = Variable(x.shape, x.axis_order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
