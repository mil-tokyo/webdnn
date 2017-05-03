from typing import Dict, Tuple

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderCNHW, OrderNHWC


class Im2Col(Operator):
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

    def __call__(self, im: Variable):
        N = im.shape_dict[Axis.N]
        H2 = (im.shape_dict[Axis.H] + 2 * self.PH - self.KH) // self.SH + 1
        W2 = (im.shape_dict[Axis.W] + 2 * self.PW - self.KW) // self.SW + 1
        C1 = im.shape_dict[Axis.C]

        out_order = self.parameters["out_order"]
        var_shape = [self.KH * self.KW * C1, N, H2, W2] if out_order == OrderCNHW else [N, H2, W2, self.KH * self.KW * C1]
        col = Variable(var_shape, out_order)

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
