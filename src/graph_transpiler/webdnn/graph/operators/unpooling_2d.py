from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.util import console


class Unpooling2D(Operator):
    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple, outsize: IntOrTuple):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)
        self.parameters["outsize"] = to_tuple(outsize)

    def __call__(self, x: Variable):
        for axis in x.order.axes:
            if axis == Axis.H or axis == Axis.W:
                continue

            self.attributes.add(Tensorwise(self, axis))

        self.append_input("x", x)
        return self.exec()

    def exec(self):
        x = self.inputs["x"]
        x_shape_dict = x.shape_dict
        N = x_shape_dict[Axis.N]
        H2 = self.parameters["outsize"][0]
        W2 = self.parameters["outsize"][1]
        C2 = x_shape_dict[Axis.C]
        y = Variable([N, H2, W2, C2], OrderNHWC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

        self.append_output("y", y)
        return y,

