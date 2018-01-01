from typing import Optional, Tuple

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.util.assertion import assert_sequence_type


class Pooling2D(Operator):
    """Pooling2D(name, ksize, stride, padding)

    Spatial pooling base operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.
        cover_all (bool, optional): If `True`, all input pixels are pooled into some output pixels.

    Signature

        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output value. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple, cover_all: bool = True):
        super().__init__(name)
        self.parameters["ksize"] = assert_sequence_type(to_tuple(ksize), (int, Placeholder), message=f"""
[Pooling2D] Parameter "ksize" must be integer or tuple of integer""")
        self.parameters["stride"] = assert_sequence_type(to_tuple(stride), (int, Placeholder), message=f"""
[Pooling2D] Parameter "stride" must be integer or tuple of integer""")
        self.parameters["padding"] = assert_sequence_type(to_tuple(padding), (int, Placeholder), message=f"""
[Pooling2D] Parameter "padding" must be integer or tuple of integer""")
        self.parameters["cover_all"] = cover_all

    def __call__(self, x: Variable):
        x_shape_dict = x.shape_dict
        N = x_shape_dict[Axis.N]
        H2 = (x_shape_dict[Axis.H] + 2 * self.PH - self.KH + (self.SH - 1 if self.cover_all else 0)) // self.SH + 1
        W2 = (x_shape_dict[Axis.W] + 2 * self.PW - self.KW + (self.SW - 1 if self.cover_all else 0)) // self.SW + 1
        C2 = x_shape_dict[Axis.C]

        y = Variable([N, H2, W2, C2], OrderNHWC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

        for axis in x.order.axes:
            if axis == Axis.H or axis == Axis.W:
                continue

            self.attributes.add(Tensorwise(axis))

        self.append_input("x", x)
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

    @property
    def cover_all(self) -> bool:
        return self.parameters["cover_all"]
