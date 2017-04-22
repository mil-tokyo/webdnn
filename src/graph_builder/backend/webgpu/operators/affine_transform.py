from typing import Dict

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


class AffineTransform(Operator):
    attributes = {PostElementwise,
                  PostAxiswise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {scale: float, bias: float}
        :param name: 
        :param parameters: 
        """
        assert "scale" in parameters
        assert "bias" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        y = Variable(x.shape, x.axis_order)
        self.append_input("x", x)
        self.append_output("y", y)

        return y,

    @property
    def scale(self) -> float:
        return self.parameters["scale"]

    @scale.setter
    def scale(self, value: float):
        self.parameters["scale"] = value

    @property
    def bias(self) -> float:
        return self.parameters["bias"]

    @bias.setter
    def bias(self, value: float):
        self.parameters["bias"] = value
