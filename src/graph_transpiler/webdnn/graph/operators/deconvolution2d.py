from typing import Tuple

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.have_weights import HaveWeights
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC
from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable


class Deconvolution2D(Operator):
    """Deconvolution2D operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.

    """

    def __init__(self, name: str, ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)
        self.attributes = {HaveWeights(self)}

    def __call__(self, x: Variable, w: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input
            w (:class:`~webdnn.graph.variable.Variable`): Filter

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict
        if PlaceHolder.check_resolved(w_shape_dict[Axis.H]) and PlaceHolder.check_resolved(w_shape_dict[Axis.W]):
            assert (w_shape_dict[Axis.H], w_shape_dict[Axis.W]) == self.ksize
        if PlaceHolder.check_resolved(w_shape_dict[Axis.C]) and PlaceHolder.check_resolved(x_shape_dict[Axis.C]):
            assert w_shape_dict[Axis.C] == x_shape_dict[Axis.C]

        N = x_shape_dict[Axis.N]
        H2 = (x_shape_dict[Axis.H] - 1) * self.SH - 2 * self.PH + self.KH
        W2 = (x_shape_dict[Axis.W] - 1) * self.SW - 2 * self.PW + self.KW
        C2 = w_shape_dict[Axis.N]

        y = Variable([N, H2, W2, C2], OrderNHWC)

        self.append_input("x", x)
        self.append_input("w", w)
        self.append_output("y", y)
        return y,

    @property
    def ksize(self) -> Tuple[int, int]:
        return self.parameters["ksize"]

    @property
    def stride(self) -> Tuple[int, int]:
        return self.parameters["stride"]

    @property
    def padding(self) -> Tuple[int, int]:
        return self.parameters["padding"]

    @property
    def KH(self) -> int:
        return self.ksize[0]

    @property
    def KW(self) -> int:
        return self.ksize[1]

    @property
    def SH(self) -> int:
        return self.stride[0]

    @property
    def SW(self) -> int:
        return self.stride[1]

    @property
    def PH(self) -> int:
        return self.padding[0]

    @property
    def PW(self) -> int:
        return self.padding[1]
