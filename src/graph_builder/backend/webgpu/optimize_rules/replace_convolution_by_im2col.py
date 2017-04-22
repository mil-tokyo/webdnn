from graph_builder.backend.webgpu.operators.im2col import Im2Col
from graph_builder.backend.webgpu.operators.sgemm import Sgemm
from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWCN
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule


class ReplaceConvolutionByIm2Col(OptimizeRule):
    """
    Convolution2DをIm2Col + sgemmに置換する
    """

    def __call__(self, graph: Operator):
        flag_changed = False
        for op in util.listup_operator_in_order(graph):
            if not isinstance(op, Convolution2D):
                continue

            op: Convolution2D

            x = op.inputs["x"]
            w = op.inputs["w"]
            old_y = op.outputs["y"]

            flag_changed = True
            op.remove_all()

            assert x.axis_order == OrderNHWC
            w.change_axis_order(OrderHWCN)
            assert old_y.axis_order == OrderNHWC

            im2col = Im2Col("im2col", {
                "ksize": op.ksize,
                "stride": op.stride,
                "padding": op.padding,
            })
            col, = im2col(x)

            sgemm = Sgemm("sgemm", {
                "M": col.shape_dict[Axis.N] * col.shape_dict[Axis.H] * col.shape_dict[Axis.W],
                "N": w.shape_dict[Axis.N],
                "K": col.shape_dict[Axis.C],
                "out_shape": [col.shape_dict[Axis.N], col.shape_dict[Axis.H], col.shape_dict[Axis.W], w.shape_dict[Axis.N]],
                "out_order": OrderNHWC,
            })
            new_y, = sgemm(col, w)

            new_y.merge(old_y)

        return graph, flag_changed
