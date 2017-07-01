from typing import Tuple

from webdnn.backend.webassembly.operators.im2col import Im2Col
from webdnn.backend.webassembly.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, OrderHWCN


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

            assert x.order == OrderNHWC
            w.change_order(OrderHWCN)
            assert old_y.order == OrderNHWC

            if op.WH != 1 or op.WW != 1 or op.stride != (1, 1) or op.padding != (0, 0):
                im2col = Im2Col(None, ksize=op.ksize, stride=op.stride, padding=op.padding, dilation_rate=op.dilation_rate)
                col, = im2col(x)
                col.change_order(OrderNHWC)

            else:
                col = x

            sgemm = Sgemm(None,
                          M=col.shape_dict[Axis.N] * col.shape_dict[Axis.H] * col.shape_dict[Axis.W],
                          N=w.shape_dict[Axis.N],
                          K=col.shape_dict[Axis.C],
                          out_shape=[col.shape_dict[Axis.N], col.shape_dict[Axis.H], col.shape_dict[Axis.W], w.shape_dict[Axis.N]],
                          out_order=OrderNHWC,
                          transpose_A=True if col.order == OrderNHWC else False,
                          transpose_B=True)
            new_y, = sgemm(col, w)

            sgemm.replace_output(new_y, old_y)

        return graph, flag_changed
