from typing import Tuple, Optional

from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.operator import Operator
from graph_transpiler.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_transpiler.graph.operators.util import IntOrTuple, to_tuple
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderNHWC


class Col2Im(Operator):
    attributes = {PostAxiswise}

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)

    def __call__(self, col: Variable):
        N = col.shape_dict[Axis.N]
        H2 = (col.shape_dict[Axis.H] - 1) * self.SH - 2 * self.PH + self.KH
        W2 = (col.shape_dict[Axis.W] - 1) * self.SW - 2 * self.PW + self.KW
        C2 = col.shape_dict[Axis.C] // self.KH // self.KW

        im = Variable([N, H2, W2, C2], OrderNHWC)

        self.append_input("col", col)
        self.append_output("im", im)

        return im,

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
