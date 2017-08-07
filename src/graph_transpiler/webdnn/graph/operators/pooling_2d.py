from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.axiswise import Axiswise
from webdnn.graph.operators.attributes.post_axiswise import PostAxiswise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.util import console


class Pooling2D(Operator):
    """Pooling2D(name, ksize, stride, padding)

    Spatial pooling base operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.

    Signature

        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output value. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)
        self.attributes.add(PostAxiswise(self, Axis.C))
        self.attributes.add(Axiswise(self, Axis.C))

    def __call__(self, x: Variable):
        x_shape_dict = x.shape_dict
        N = x_shape_dict[Axis.N]
        H2 = (x_shape_dict[Axis.H] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) // self.parameters["stride"][0] + 1
        W2 = (x_shape_dict[Axis.W] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) // self.parameters["stride"][1] + 1
        C2 = x_shape_dict[Axis.C]
        if ((x_shape_dict[Axis.H] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) % self.parameters["stride"][0] != 0) or \
            ((x_shape_dict[Axis.W] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) % self.parameters["stride"][1] != 0):
            # https://github.com/fchollet/keras/issues/5090#issuecomment-279495401
            console.warning(
                "[Pooling2D] Performing pooling with parameters which causes edge is ignored. " +
                "Which edge (left / right) is ignored is different on frameworks," +
                " so slightly different result will be generated.")

        y = Variable([N, H2, W2, C2], OrderNHWC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

        self.append_input("x", x)
        self.append_output("y", y)
        return y,
