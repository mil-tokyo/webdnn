from typing import Dict

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.axiswise import Axiswise
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


class AxiswiseScale(Operator):
    """
    Channelwiseにウェイトを乗算するレイヤー
    """
    attributes = {PostElementwise,
                  PostAxiswise,
                  Axiswise,
                  Inplace,
                  HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {axis: Axis}
        :param name: 
        :param parameters: 
        """
        assert "axis" in parameters
        assert isinstance(parameters["axis"], Axis)
        super().__init__(name, parameters)

    def __call__(self, x: Variable, s: Variable):
        assert s.ndim == 1
        assert x.shape_dict[self.parameters["axis"]] == s.size
        y = Variable(x.shape, x.axis_order)
        self.append_input("x", x)
        self.append_input("s", s)
        self.append_output("y", y)
        return y,
