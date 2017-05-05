from typing import Dict, Tuple

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNCHW


class Deconvolution2D(Operator):
    """
    Deconvolutionレイヤー(bias含まず)
    """
    attributes = {PostElementwise,
                  PostAxiswise,
                  HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        weights["W"]: (kh, kw, in_size, out_size)
        parameters: {ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int], cover_all: Boolean=False}
        :param name: 
        :param parameters: 
        """
        assert "ksize" in parameters
        assert "stride" in parameters
        assert "padding" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict
        assert (w_shape_dict[Axis.H], w_shape_dict[Axis.W]) == self.ksize
        assert w_shape_dict[Axis.C] == x_shape_dict[Axis.C]

        N = x_shape_dict[Axis.N]
        H2 = (x_shape_dict[Axis.H] - 1) * self.SH - 2 * self.PH + self.KH
        W2 = (x_shape_dict[Axis.W] - 1) * self.SW - 2 * self.PW + self.KW
        C2 = w_shape_dict[Axis.N]

        y = Variable([N, C2, H2, W2], OrderNCHW)
        y.change_axis_order(x.axis_order)  # FIXME: need this?

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
