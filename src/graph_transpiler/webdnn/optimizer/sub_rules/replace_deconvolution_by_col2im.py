from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, Order
from webdnn.util.misc import mul


class ReplaceDeconvolutionByCol2Im(OptimizeRule):
    """
    Replace Deconvolution2D by Tensordot and Col2Im
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Deconvolution2D):  # type: Deconvolution2D
            x = op.inputs["x"]
            w = op.inputs["w"]
            y = op.outputs["y"]
            flag_changed = True
            op.remove_all()

            a_filter, a_kh, a_kw = Axis(), Axis(), Axis()
            w, = ReinterpretAxis(None, in_order=OrderNHWC, out_order=Order([Axis.C, a_kh, a_kw, a_filter]))(w)
            if op.KH == 1 and op.KW == 1 and op.stride == (1, 1) and op.padding == (0, 0):
                # Projection
                w = w.transpose(Order([Axis.C, a_kh, a_kw, a_filter]))
                w = w.reshape([w.shape_dict[Axis.C], w.shape_dict[a_filter]], Order([Axis.C, a_filter]))
                new_y, = Tensordot(None, [Axis.C, a_filter])(x, w)

            else:
                # General deconvolution
                w = w.transpose(Order([a_filter, a_kh, a_kw, Axis.C]))
                col, = Tensordot(None, axes=[Axis.C, a_filter])(x, w)
                col = col.transpose(Order([Axis.N, Axis.H, Axis.W, a_kh, a_kw, Axis.C]))
                col = col.reshape(shape=[*col.shape[0:3], mul(col.shape[3:6])], order=OrderNHWC)

                new_y, = Col2Im(None, ksize=op.ksize, stride=op.stride, padding=op.padding)(col)

            OptimizeRule.replace_variable(graph, new_y.transpose_like(y), y)

        return graph, flag_changed
