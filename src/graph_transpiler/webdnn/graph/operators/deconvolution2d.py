from typing import Tuple, Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC, OrderNCHW, Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.util.assertion import assert_sequence_type


class Deconvolution2D(Operator):
    """Deconvolution2D(name, ksize, stride, padding)

    Spatial deconvolution operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.

    Signature
        .. code::

            y, = op(x, w)

        - **x** - Input variables. It must has 4 axes, :obj:`~webdnn.Axis.N`, :obj:`~webdnn.Axis.C`,
          :obj:`~webdnn.Axis.H`, and :obj:`~webdnn.Axis.W`.
        - **w** - Kernel variable. It must has :obj:`~webdnn.graph.axis.Axis.N`, :obj:`~webdnn.Axis.C`,
          :obj:`~webdnn.Axis.H`, :obj:`~webdnn.Axis.W`. Its size of :obj:`~webdnn.Axis.H` and
          :obj:`~webdnn.Axis.W` must be same as kernel size. Its size of :obj:`~webdnn.Axis.C` must be same as
          :code:`x`.
        - **y** - Output variable. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple):
        super().__init__(name)
        self.parameters["ksize"] = assert_sequence_type(to_tuple(ksize), (int, Placeholder), message=f"""
[Deconvolution2D] Parameter "ksize" must be integer or tuple of integer""")
        self.parameters["stride"] = assert_sequence_type(to_tuple(stride), (int, Placeholder), message=f"""
[Deconvolution2D] Parameter "stride" must be integer or tuple of integer""")
        self.parameters["padding"] = assert_sequence_type(to_tuple(padding), (int, Placeholder), message=f"""
[Deconvolution2D] Parameter "padding" must be integer or tuple of integer""")
        self.attributes.add(Tensorwise(Axis.N))

    def __call__(self, x: Variable, w: Variable):
        assert x.order.check_same_axes(OrderNCHW), f"""
[Deconvolution2D] Input variable of Deconvolution2D must have N, C, H, and W axes:
    (x.order.axes) = {x.order.axes}"""

        assert w.order.check_same_axes(Order([Axis.N, Axis.KH, Axis.KW, Axis.C])), f"""
[Deconvolution2D] Kernel variable of Deconvolution2D must have N, C, KH, and KW axes:
    (w.order.axes) = {w.order.axes}"""

        if Placeholder.check_resolved(w.shape_dict[Axis.KH]) and Placeholder.check_resolved(w.shape_dict[Axis.KW]):
            assert (w.shape_dict[Axis.KH], w.shape_dict[Axis.KW]) == self.ksize, f"""
[Deconvolution2D] Kernel variable of Deconvolution2D must be same spatial size as ksize parameter:
    (w.shape_dict[Axis.KH]) = {w.shape_dict[Axis.KH]}
    (w.shape_dict[Axis.KW]) = {w.shape_dict[Axis.KW]}
    (self.ksize) = {self.ksize}"""

        if Placeholder.check_resolved(w.shape_dict[Axis.C]) and Placeholder.check_resolved(x.shape_dict[Axis.C]):
            assert w.shape_dict[Axis.C] == x.shape_dict[Axis.C], f"""
[Deconvolution2D] Input and Kernel variables of Deconvolution2D must be same channel size:
    (x.shape_dict[Axis.C]) = {x.shape_dict[Axis.C]}
    (w.shape_dict[Axis.C]) = {w.shape_dict[Axis.C]}"""

        N = x.shape_dict[Axis.N]
        H2 = (x.shape_dict[Axis.H] - 1) * self.SH - 2 * self.PH + self.KH
        W2 = (x.shape_dict[Axis.W] - 1) * self.SW - 2 * self.PW + self.KW
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
