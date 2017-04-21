from typing import Dict, Tuple

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA


class Im2Col(Operator):
    attributes = {}  # TODO

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
        x_shape_dict = im.shape_dict
        N = x_shape_dict[A.Axis.N]
        H2 = (x_shape_dict[A.Axis.H] + 2 * self.PH - self.KH) // self.SH + 1
        W2 = (x_shape_dict[A.Axis.W] + 2 * self.PW - self.KW) // self.SW + 1
        C1 = x_shape_dict[A.Axis.C]

        var_shape = [N, H2, W2, self.KH * self.KW * C1]
        col = Variable(var_shape, VA.OrderNHWC)

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
