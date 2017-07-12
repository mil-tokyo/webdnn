from typing import Tuple, Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.have_weights import HaveWeights
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable


class Convolution2D(Operator):
    """Convolution2D operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.
        dilation_rate (int or tuple of int): Dilation rate. 1 means ordinary convolution.
         Input pixels are shifted by (dilation_rate - 1) pixels.

    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple,
                 dilation_rate: Optional[IntOrTuple] = 1):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)
        self.parameters["dilation_rate"] = to_tuple(dilation_rate)
        self.attributes = {HaveWeights(self)}

    def __call__(self, x: Variable, w: Variable) -> Tuple[Variable]:
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input
            w (:class:`~webdnn.graph.variable.Variable`): Filter

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict

        if Placeholder.check_resolved(w_shape_dict[Axis.H]) and Placeholder.check_resolved(w_shape_dict[Axis.W]):
            assert (w_shape_dict[Axis.H], w_shape_dict[Axis.W]) == self.ksize
        if Placeholder.check_resolved(w_shape_dict[Axis.C]) and Placeholder.check_resolved(x_shape_dict[Axis.C]):
            assert w_shape_dict[Axis.C] == x_shape_dict[Axis.C]

        N = x_shape_dict[Axis.N]
        H2 = (x_shape_dict[Axis.H] + 2 * self.PH - self.WH) // self.SH + 1
        W2 = (x_shape_dict[Axis.W] + 2 * self.PW - self.WW) // self.SW + 1
        C2 = w_shape_dict[Axis.N]

        y = Variable([N, H2, W2, C2], OrderNHWC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

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
    def dilation_rate(self) -> Tuple[int, int]:
        return self.parameters["dilation_rate"]

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

    @property
    def DH(self) -> int:
        return self.dilation_rate[0]

    @property
    def DW(self) -> int:
        return self.dilation_rate[1]

    @property
    def WH(self) -> int:
        """
        Input window height considering dilation.
        Returns:

        """
        return self.DH * (self.KH - 1) + 1

    @property
    def WW(self) -> int:
        """
        Input window width considering dilation.
        Returns:

        """
        return self.DW * (self.KW - 1) + 1
