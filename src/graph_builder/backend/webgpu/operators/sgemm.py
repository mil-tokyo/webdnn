from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA


class Sgemm(Operator):
    attributes = {}  # FIXME

    def __init__(self, name: str, parameters: Dict[str, object] = None):
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        self.append_input("x", x)
        self.append_input("w", w)

        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict

        assert x_shape_dict[A.Axis.C] == w_shape_dict[A.Axis.H] * w_shape_dict[A.Axis.W] * w_shape_dict[A.Axis.C]

        assert x.axis_order == VA.OrderNHWC, \
            "Input variable for WebGPU.Sgemm Operator must be HWCN data order." \
            f"Actual data order is {x.axis_order}"

        w.change_axis_order(VA.OrderHWCN)

        y = Variable([
            x_shape_dict[A.Axis.N],
            x_shape_dict[A.Axis.H],
            x_shape_dict[A.Axis.W],
            w_shape_dict[A.Axis.N]
        ], VA.OrderNHWC)

        self.append_output("y", y)

        return y,
