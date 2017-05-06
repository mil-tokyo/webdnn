from typing import Tuple, Optional

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.operators.util import IntOrTuple, to_tuple
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC


class Convolution2D(Operator):
    """Convolution2D operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.

    """
    attributes = {PostElementwise,
                  PostAxiswise,
                  HaveWeights}

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)

    def __call__(self, x: Variable, w: Variable) -> Tuple[Variable]:
        """
        Args:
            x (:class:`~graph_builder.graph.variable.Variable`): Input
            w (:class:`~graph_builder.graph.variable.Variable`): Filter

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict

        assert (w_shape_dict[Axis.H], w_shape_dict[Axis.W]) == self.ksize
        assert w_shape_dict[Axis.C] == x_shape_dict[Axis.C]

        N = x_shape_dict[Axis.N]
        H2 = (x_shape_dict[Axis.H] + 2 * self.PH - self.KH) // self.SH + 1
        W2 = (x_shape_dict[Axis.W] + 2 * self.PW - self.KW) // self.SW + 1
        C2 = w_shape_dict[Axis.N]

        y = Variable([N, H2, W2, C2], OrderNHWC)

        self.append_input("x", x)
        self.append_input("w", w)
        self.append_output("y", y)
        return y,

    @property
    def ksize(self) -> Tuple[int, int]:
        """
        (Tuple[int, int]): Kernel size. The first element is height, and the second element is width of the kernel.
        """
        return self.parameters["ksize"]

    @property
    def stride(self) -> Tuple[int, int]:
        """
        (Tuple[int, int]): Stride size. The first element is height, and the second element is width of the stride.
        """
        return self.parameters["stride"]

    @property
    def padding(self) -> Tuple[int, int]:
        """
        (Tuple[int, int]): Padding size. The first element is height, and the second element is width of the padding.
        """
        return self.parameters["padding"]

    @property
    def KH(self) -> int:
        """
        (int): Height of the kernel
        """
        return self.ksize[0]

    @property
    def KW(self) -> int:
        """
        (int): Width of the kernel
        """
        return self.ksize[1]

    @property
    def SH(self) -> int:
        """
        (int): Height of the stride
        """
        return self.stride[0]

    @property
    def SW(self) -> int:
        """
        (int): Width of the stride
        """
        return self.stride[1]

    @property
    def PH(self) -> int:
        """
        (int): Height of the padding
        """
        return self.padding[0]

    @property
    def PW(self) -> int:
        """
        (int): Width of the padding
        """
        return self.padding[1]
