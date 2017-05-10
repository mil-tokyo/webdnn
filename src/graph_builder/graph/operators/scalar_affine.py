from typing import Optional

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


# FIXME: rename
class ScalarAffine(Operator):
    attributes = {PostElementwise,
                  PostAxiswise}

    def __init__(self, name: Optional[str], scale: float, bias: float):
        super().__init__(name)
        self.scale = scale
        self.bias = bias

    def __call__(self, x: Variable):
        y = Variable(x.shape, x.order)
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
