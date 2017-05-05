from typing import Tuple

from graph_builder.backend.webgpu.operators.col2im import Col2Im
from graph_builder.backend.webgpu.operators.sgemm import Sgemm
from graph_builder.graph.axis import Axis
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.deconvolution2d import Deconvolution2D
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderCHWN
from graph_builder.optimize_rule import util
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class ReplaceDeconvolutionByCol2Im(OptimizeRule):
    """
    Deconvolution2Dをsgemm + Col2Imに置換する
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in util.listup_operators(graph):
            if not isinstance(op, Deconvolution2D):
                continue

            op: Deconvolution2D

            x = op.inputs["x"]
            w = op.inputs["w"]
            old_y = op.outputs["y"]

            flag_changed = True
            op.remove_all()

            assert old_y.axis_order == OrderNHWC
            w.change_axis_order(OrderCHWN)
            assert old_y.axis_order == OrderNHWC

            sgemm = Sgemm("sgemm_nhwc", {
                "M": x.shape_dict[Axis.N] * x.shape_dict[Axis.H] * x.shape_dict[Axis.W],
                "N": w.shape_dict[Axis.H] * w.shape_dict[Axis.W] * w.shape_dict[Axis.N],
                "K": x.shape_dict[Axis.C],
                "out_shape": [x.shape_dict[Axis.N],
                              x.shape_dict[Axis.H],
                              x.shape_dict[Axis.W],
                              w.shape_dict[Axis.H] * w.shape_dict[Axis.W] * w.shape_dict[Axis.N],
                              ],
                "out_order": OrderNHWC,
                "transpose_A": True if x.axis_order == OrderNHWC else False,
                "transpose_B": True
            })
            col, = sgemm(x, w)

            col2im = Col2Im("col2im", {
                "ksize": op.ksize,
                "stride": op.stride,
                "padding": op.padding,
            })
            new_y, = col2im(col)
            new_y.change_axis_order(old_y.axis_order)

            new_y.merge(old_y)

        return graph, flag_changed
