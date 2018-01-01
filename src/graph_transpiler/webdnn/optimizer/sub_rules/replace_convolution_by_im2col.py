from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, Order


class ReplaceConvolutionByIm2Col(OptimizeRule):
    """
    Replace Convolution2D by Im2Col and Tensordot
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Convolution2D):
            x = op.inputs["x"]
            w = op.inputs["w"]
            y = op.outputs["y"]
            flag_changed = True
            op.remove_all()

            a_filter = Axis()
            w, = ReinterpretAxis(None,
                                 in_order=Order([Axis.N, Axis.KH, Axis.KW, Axis.C]),
                                 out_order=Order([Axis.C, Axis.KH, Axis.KW, a_filter]))(w)

            if op.WH == 1 and op.WW == 1 and op.stride == (1, 1) and op.padding == (0, 0):
                # Projection
                new_y, = Tensordot(None, [[Axis.C], [Axis.KH, Axis.KW, a_filter]])(x, w)

            elif op.WH == x.shape_dict[Axis.H] and op.WW == x.shape_dict[Axis.W] and op.padding == (0, 0):
                # Global convolution
                col, = ReinterpretAxis(None, in_order=OrderNHWC, out_order=Order([Axis.N, Axis.KH, Axis.KW, a_filter]))(x)
                new_y, = Tensordot(None, [[Axis.KH, Axis.KW, a_filter], [Axis.KH, Axis.KW, a_filter]])(col, w)

            else:
                # General convolution
                col, = Im2Col(None, ksize=op.ksize, stride=op.stride, padding=op.padding, dilation_rate=op.dilation_rate)(x)
                new_y, = Tensordot(None, [[Axis.KH, Axis.KW, Axis.C], [Axis.KH, Axis.KW, a_filter]])(col, w)

            new_y = new_y.transpose(y.order)
            OptimizeRule.replace_variable(graph, new_y, y)

        return graph, flag_changed
