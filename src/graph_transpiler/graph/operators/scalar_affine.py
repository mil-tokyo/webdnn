from typing import Optional

from graph_transpiler.graph.operator import Operator
from graph_transpiler.graph.operators.attributes.elementwise import Elementwise
from graph_transpiler.graph.operators.attributes.inplace import Inplace
from graph_transpiler.graph.variable import Variable


class ScalarAffine(Operator):
    def __init__(self, name: Optional[str], scale: float, bias: float):
        super().__init__(name)
        self.scale = scale
        self.bias = bias
        self.attributes = {Elementwise(self),
                           Inplace(self, "x", "y")}

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
