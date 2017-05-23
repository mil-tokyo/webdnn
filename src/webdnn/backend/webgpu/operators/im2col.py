from typing import Tuple, Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


class Im2Col(Operator):
    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)

    def __call__(self, im: Variable):
        N = im.shape_dict[Axis.N]
        H2 = (im.shape_dict[Axis.H] + 2 * self.PH - self.KH) // self.SH + 1
        W2 = (im.shape_dict[Axis.W] + 2 * self.PW - self.KW) // self.SW + 1
        C1 = im.shape_dict[Axis.C]

        col = Variable([N, H2, W2, self.KH * self.KW * C1], OrderNHWC)

        self.append_input("im", im)
        self.append_output("col", col)

        return col,

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
        return self.parameters["ksize"][0]

    @property
    def KW(self) -> int:
        return self.parameters["ksize"][1]

    @property
    def SH(self) -> int:
        return self.parameters["stride"][0]

    @property
    def SW(self) -> int:
        return self.parameters["stride"][1]

    @property
    def PH(self) -> int:
        return self.parameters["padding"][0]

    @property
    def PW(self) -> int:
        return self.parameters["padding"][1]
