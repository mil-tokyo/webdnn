from typing import Tuple

from webdnn.backend.webassembly.operators.col2im import Col2Im
from webdnn.backend.webassembly.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, OrderCHWN


class ReplaceDeconvolutionByCol2Im(OptimizeRule):
    """
    Deconvolution2Dをsgemm + Col2Imに置換する
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.listup_operators(graph):
            if not isinstance(op, Deconvolution2D):
                continue

            op: Deconvolution2D

            x = op.inputs["x"]
            w = op.inputs["w"]
            old_y = op.outputs["y"]

            flag_changed = True
            op.remove_all()

            assert old_y.order == OrderNHWC
            w.change_order(OrderCHWN)
            assert old_y.order == OrderNHWC

            sgemm = Sgemm(None,
                          M=x.shape_dict[Axis.N] * x.shape_dict[Axis.H] * x.shape_dict[Axis.W],
                          N=w.shape_dict[Axis.H] * w.shape_dict[Axis.W] * w.shape_dict[Axis.N],
                          K=x.shape_dict[Axis.C],
                          out_shape=[x.shape_dict[Axis.N],
                                     x.shape_dict[Axis.H],
                                     x.shape_dict[Axis.W],
                                     w.shape_dict[Axis.H] * w.shape_dict[Axis.W] * w.shape_dict[Axis.N],
                                     ],
                          out_order=OrderNHWC,
                          transpose_A=True if x.order == OrderNHWC else False,
                          transpose_B=True)
            col, = sgemm(x, w)

            col2im = Col2Im(None, ksize=op.ksize, stride=op.stride, padding=op.padding)
            new_y, = col2im(col)

            col2im.replace_output(new_y, old_y)

        return graph, flag_changed
