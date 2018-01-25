from typing import Tuple, Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC, OrderNCHW, Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.util.assertion import assert_sequence_type


class Convolution2D(Operator):
    """Convolution2D(name, ksize, stride, padding, dilation_rate=1)

    Spatial convolution operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.
        dilation_rate (int or tuple of int): Dilation rate. 1 means ordinary convolution.
         Input pixels are shifted by (dilation_rate - 1) pixels.

    Signature
        .. code::

            y, = op(x, w)

        - **x** - Input variables. It must has 4 axes, :obj:`~webdnn.Axis.N`, :obj:`~webdnn.Axis.C`,
          :obj:`~webdnn.Axis.H`, and :obj:`~webdnn.Axis.W`.
        - **w** - Kernel variable. It must has :obj:`~webdnn.Axis.N`, :obj:`~webdnn.Axis.C`,
          :obj:`~webdnn.Axis.H`, :obj:`~webdnn.Axis.W`. Its size of :obj:`~webdnn.Axis.H` and
          :obj:`~webdnn.Axis.W` must be same as kernel size. Its size of :obj:`~webdnn.Axis.C` must be same as
          :code:`x`.
        - **y** - Output variable. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple,
                 dilation_rate: Optional[IntOrTuple] = 1):
        super().__init__(name)
        self.parameters["ksize"] = assert_sequence_type(to_tuple(ksize), (int, Placeholder), message=f"""
[Convolution2D] Parameter "ksize" must be integer or tuple of integer""")
        self.parameters["stride"] = assert_sequence_type(to_tuple(stride), (int, Placeholder), message=f"""
[Convolution2D] Parameter "stride" must be integer or tuple of integer""")
        self.parameters["padding"] = assert_sequence_type(to_tuple(padding), (int, Placeholder), message=f"""
[Convolution2D] Parameter "padding" must be integer or tuple of integer""")
        self.parameters["dilation_rate"] = assert_sequence_type(to_tuple(dilation_rate), (int, Placeholder), message=f"""
[Convolution2D] Parameter "dilation_rate" must be integer or tuple of integer""")
        self.attributes.add(Tensorwise(Axis.N))

    def __call__(self, x: Variable, w: Variable) -> Tuple[Variable]:
        assert x.order.check_same_axes(OrderNCHW), f"""
[Convolution2D] Input variable of Convolution2D must have N, C, H, and W axes:
    (x.order.axes) = {x.order.axes}"""

        assert w.order.check_same_axes(Order([Axis.N, Axis.KH, Axis.KW, Axis.C])), f"""
[Convolution2D] Kernel variable of Convolution2D must have N, C, KH, and KW axes:
    (w.order.axes) = {w.order.axes}"""

        if Placeholder.check_resolved(w.shape_dict[Axis.KH]) and Placeholder.check_resolved(w.shape_dict[Axis.KW]):
            assert (w.shape_dict[Axis.KH], w.shape_dict[Axis.KW]) == self.ksize, f"""
[Convolution2D] Kernel variable of Convolution2D must be same spatial size as ksize parameter:
    (w.shape_dict[Axis.KH]) = {w.shape_dict[Axis.KH]}
    (w.shape_dict[Axis.KW]) = {w.shape_dict[Axis.KW]}
    (self.ksize) = {self.ksize}"""

        if Placeholder.check_resolved(w.shape_dict[Axis.C]) and Placeholder.check_resolved(x.shape_dict[Axis.C]):
            assert w.shape_dict[Axis.C] == x.shape_dict[Axis.C], f"""
[Convolution2D] Input and Kernel variables of Convolution2D must be same channel size:
    (x.shape_dict[Axis.C]) = {x.shape_dict[Axis.C]}
    (w.shape_dict[Axis.C]) = {w.shape_dict[Axis.C]}"""

        N = x.shape_dict[Axis.N]
        H2 = (x.shape_dict[Axis.H] + 2 * self.PH - self.WH) // self.SH + 1
        W2 = (x.shape_dict[Axis.W] + 2 * self.PW - self.WW) // self.SW + 1
        C2 = w.shape_dict[Axis.N]

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
        return self.DH * (self.KH - 1) + 1

    @property
    def WW(self) -> int:
        return self.DW * (self.KW - 1) + 1
