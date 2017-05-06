from typing import Tuple

from graph_builder.backend.webgpu.operators.im2col import Im2Col
from graph_builder.backend.webgpu.operators.sgemm import Sgemm
from graph_builder.graph import traverse
from graph_builder.graph.axis import Axis
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.optimize_rule import OptimizeRule
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWCN


class ReplaceConvolutionByIm2Col(OptimizeRule):
    """
    Convolution2DをIm2Col + sgemmに置換する
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.listup_operators(graph):
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

            if op.ksize[0] > 1 or op.ksize[1] > 1 or op.stride[0] > 1 or op.stride[1] > 1 or op.padding[0] > 0 or op.padding[1] > 0:
                im2col = Im2Col(None, ksize=op.ksize, stride=op.stride, padding=op.padding)
                col, = im2col(x)
                col.change_axis_order(OrderNHWC)

            else:
                col = x

            sgemm = Sgemm(None,
                          M=col.shape_dict[Axis.N] * col.shape_dict[Axis.H] * col.shape_dict[Axis.W],
                          N=w.shape_dict[Axis.N],
                          K=col.shape_dict[Axis.C],
                          out_shape=[col.shape_dict[Axis.N], col.shape_dict[Axis.H], col.shape_dict[Axis.W], w.shape_dict[Axis.N]],
                          out_order=OrderNHWC,
                          transpose_A=True if col.axis_order == OrderNHWC else False,
                          transpose_B=True)
            new_y, = sgemm(col, w)

            new_y.merge(old_y)

        return graph, flag_changed
