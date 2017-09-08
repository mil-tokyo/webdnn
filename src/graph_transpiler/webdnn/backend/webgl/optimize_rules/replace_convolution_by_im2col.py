from typing import Tuple

import numpy as np

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.operators.im2col import Im2Col
from webdnn.backend.webgl.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, OrderNC
from webdnn.graph.variables.constant_variable import ConstantVariable


class ReplaceConvolutionByIm2Col(OptimizeRule):
    """
    Replace Convolution2D with Im2Col and SGEMM
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Convolution2D):  # type: Convolution2D
            x = op.inputs["x"]
            w = op.inputs["w"]  # type: ConstantVariable
            old_y = op.outputs["y"]

            flag_changed = True
            op.remove_all()

            assert x.order == OrderNHWC
            assert isinstance(w, ConstantVariable)
            assert old_y.order == OrderNHWC

            w.change_order(OrderNHWC)

            col, = Im2Col(None, ksize=op.ksize, stride=op.stride, padding=op.padding, dilation_rate=op.dilation_rate)(x)
            col.change_order(OrderNHWC)
            ChannelMode.set(col, ChannelModeEnum.R)

            M = col.shape_dict[Axis.N] * col.shape_dict[Axis.H] * col.shape_dict[Axis.W]
            N = w.shape_dict[Axis.N]
            K = col.shape_dict[Axis.C]

            if K > (w.size // N):
                w2_data = np.hstack([w.data.reshape(N, w.size // N), np.zeros([N, K - w.size // N])])
            else:
                w2_data = w.data.reshape(N, w.size // N)

            w = ConstantVariable(w2_data, OrderNC)
            ChannelMode.set(w, ChannelModeEnum.R)

            sgemm = Sgemm(None, M=M, N=N, K=K,
                          out_shape=[col.shape_dict[Axis.N], col.shape_dict[Axis.H], col.shape_dict[Axis.W], w.shape_dict[Axis.N]],
                          out_order=OrderNHWC,
                          transpose_A=True,
                          transpose_B=False)
            new_y, = sgemm(col, w)

            sgemm.replace_output(new_y, old_y)

        return graph, flag_changed
