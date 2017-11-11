from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.sgemm import Sgemm
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, OrderHWCN


class ReplaceConvolutionByIm2Col(OptimizeRule):
    """
    Replace Convolution2D by Im2Col and SGEMM
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Convolution2D):  # type: Convolution2D
            x = op.inputs["x"]
            w = op.inputs["w"]
            y = op.outputs["y"]

            flag_changed = True
            op.remove_all()
            w.change_order(OrderHWCN)
            transpose_B = True

            if op.WH == 1 and op.WW == 1 and op.stride == (1, 1) and op.padding == (0, 0):
                # Projection
                col = x
                col.change_order(OrderNHWC)
                transpose_A = True

            elif op.WH == x.shape_dict[Axis.H] and op.WW == x.shape_dict[Axis.W] and op.padding == (0, 0):
                # Global convolution
                col = x
                col.change_order(OrderNHWC)
                transpose_A = True

            else:
                # General convolution
                col, = Im2Col(None, ksize=op.ksize, stride=op.stride, padding=op.padding, dilation_rate=op.dilation_rate)(x)
                col.change_order(OrderNHWC)
                transpose_A = True

            new_y, = Sgemm(None,
                           M=col.shape_dict[Axis.N] * col.shape_dict[Axis.H] * col.shape_dict[Axis.W],
                           N=w.shape_dict[Axis.N],
                           K=col.shape_dict[Axis.C],
                           out_shape=[col.shape_dict[Axis.N], col.shape_dict[Axis.H], col.shape_dict[Axis.W], w.shape_dict[Axis.N]],
                           out_order=OrderNHWC,
                           transpose_A=transpose_A, transpose_B=transpose_B)(col, w)

            new_y = new_y.transpose(y.order)
            OptimizeRule.replace_variable(graph, new_y, y)

        return graph, flag_changed
