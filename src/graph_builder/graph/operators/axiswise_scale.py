from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class AxiswiseScale(Operator):
    """
    Channelwiseにウェイトを乗算するレイヤー
    """
    attributes = {A.PostElementwise,
                  A.PostAxiswise,
                  A.Axiswise,
                  A.Inplace,
                  A.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {axis: A.Axis}
        :param name: 
        :param parameters: 
        """
        assert "axis" in parameters
        assert isinstance(parameters["axis"], A.Axis)
        super().__init__(name, parameters)

    def __call__(self, x: Variable, s: Variable):
        assert s.ndim == 1
        assert x.shape_dict[self.parameters["axis"]] == s.size
        y = Variable(x.shape, x.axis_order)
        self.append_input("x", x)
        self.append_input("s", s)
        self.append_output("y", y)
        return y,
