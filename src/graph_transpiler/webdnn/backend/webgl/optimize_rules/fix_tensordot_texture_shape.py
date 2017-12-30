from typing import Tuple

from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util.misc import mul


class FixTensordotTextureShape(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Tensordot):
            A = op.inputs["A"]
            B = op.inputs["B"]
            axes = op.axes
            K = mul(A.shape_dict[a] for a in axes[0])
            M = A.size // K
            N = B.size // K

            if K % 4 == 0:
                if ChannelMode.get(A) != ChannelModeEnum.RGBA:
                    flag_changed = True
                    ChannelMode.set(A, ChannelModeEnum.RGBA)

                if ChannelMode.get(B) != ChannelModeEnum.RGBA:
                    flag_changed = True
                    ChannelMode.set(B, ChannelModeEnum.RGBA)

            else:
                if ChannelMode.get(A) != ChannelModeEnum.R:
                    flag_changed = True
                    ChannelMode.set(A, ChannelModeEnum.R)

                if ChannelMode.get(B) != ChannelModeEnum.R:
                    flag_changed = True
                    ChannelMode.set(B, ChannelModeEnum.R)

            if TextureShape.get(A) != (M, K):
                flag_changed = True
                TextureShape.set(A, height=M, width=K)

            if TextureShape.get(B) != (N, K):
                flag_changed = True
                TextureShape.set(B, height=N, width=K)

        return graph, flag_changed
