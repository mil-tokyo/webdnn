from typing import Dict

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWCN


class Sgemm(Operator):
    attributes = {PostElementwise,
                  PostAxiswise,
                  HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object] = None):
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        self.append_input("x", x)
        self.append_input("w", w)

        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict

        assert x_shape_dict[Axis.C] == w_shape_dict[Axis.H] * w_shape_dict[Axis.W] * w_shape_dict[Axis.C]

        assert x.axis_order == OrderNHWC, \
            "Input variable for WebGPU.Sgemm Operator must be HWCN data order." \
            f"Actual data order is {x.axis_order}"

        w.change_axis_order(OrderHWCN)

        y = Variable([
            x_shape_dict[Axis.N],
            x_shape_dict[Axis.H],
            x_shape_dict[Axis.W],
            w_shape_dict[Axis.N]
        ], OrderNHWC)

        self.append_output("y", y)

        return y,
