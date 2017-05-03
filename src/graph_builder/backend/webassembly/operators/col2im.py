from typing import Dict, Tuple

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderCNHW


class Col2Im(Operator):
    attributes = {PostElementwise,
                  PostAxiswise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int]}
        :param name: 
        :param parameters: 
        """
        assert "ksize" in parameters
        assert "stride" in parameters
        assert "padding" in parameters
        super().__init__(name, parameters)

    def __call__(self, col: Variable):
        assert col.axis_order == OrderNHWC

        N = col.shape_dict[Axis.N]
        H2 = (col.shape_dict[Axis.H] - 1) * self.SH - 2 * self.PH + self.KH
        W2 = (col.shape_dict[Axis.W] - 1) * self.SW - 2 * self.PW + self.KW
        C2 = col.shape_dict[Axis.C] // self.KH // self.KW

        var_shape = [N, H2, W2, C2]
        im = Variable(var_shape, OrderNHWC)

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
