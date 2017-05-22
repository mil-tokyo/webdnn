from typing import Tuple

from graph_transpiler.backend.webgpu.operators.col2im import Col2Im
from graph_transpiler.backend.webgpu.operators.sgemm import Sgemm
from graph_transpiler.graph import traverse
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.operators.deconvolution2d import Deconvolution2D
from graph_transpiler.graph.optimize_rule import OptimizeRule
from graph_transpiler.graph.variables.attributes.order import OrderNHWC, OrderCHWN, OrderCNHW


class ReplaceDeconvolutionByCol2Im(OptimizeRule):
    """
    Deconvolution2Dをsgemm + Col2Imに置換する
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Deconvolution2D):  # type: Deconvolution2D
            x = op.inputs["x"]
            w = op.inputs["w"]
            old_y = op.outputs["y"]

            flag_changed = True
            op.remove_all()

            assert x.order == OrderNHWC or x.order == OrderCNHW
            w.change_order(OrderCHWN)
            assert old_y.order == OrderNHWC

            sgemm = Sgemm(None,
                          M=x.shape_dict[Axis.N] * x.shape_dict[Axis.H] * x.shape_dict[Axis.W],
                          N=w.shape_dict[Axis.H] * w.shape_dict[Axis.W] * w.shape_dict[Axis.N],
                          K=x.shape_dict[Axis.C],
                          out_shape=[x.shape_dict[Axis.N],
                                     x.shape_dict[Axis.H],
                                     x.shape_dict[Axis.W],
                                     w.shape_dict[Axis.H] * w.shape_dict[Axis.W] * w.shape_dict[Axis.N]],
                          out_order=OrderNHWC,
                          transpose_A=True if x.order == OrderNHWC else False,
                          transpose_B=True)
            col, = sgemm(x, w)

            col2im = Col2Im(None, ksize=op.ksize, stride=op.stride, padding=op.padding)
            new_y, = col2im(col)
            new_y.change_order(old_y.order)

            col2im.replace_output(new_y, old_y)

        return graph, flag_changed
