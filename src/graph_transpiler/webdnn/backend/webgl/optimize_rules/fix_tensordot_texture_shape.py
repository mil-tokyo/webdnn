from typing import Tuple

from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util.misc import mul


class FixTensordotTextureShape(OptimizeRule):
    def __init__(self, optimize_channel_mode: bool = False):
        super(FixTensordotTextureShape, self).__init__()
        self.optimize_channel_mode = optimize_channel_mode

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Tensordot):  # type: Tensordot
            A = op.inputs["A"]
            B = op.inputs["B"]
            axes = op.axes
            K = mul(A.shape[-len(axes[0]):])
            M = A.size // K
            N = B.size // K

            if all([self.optimize_channel_mode,
                    K % 4 == 0]):
                if ChannelMode.get(A) != ChannelModeEnum.RGBA:
                    flag_changed = True
                    ChannelMode.set(A, ChannelModeEnum.RGBA)

                if ChannelMode.get(B) != ChannelModeEnum.RGBA:
                    flag_changed = True
                    ChannelMode.set(B, ChannelModeEnum.RGBA)

                texture_shape_A = [M, K // 4]
                texture_shape_B = [N, K // 4]

            else:
                if ChannelMode.get(A) != ChannelModeEnum.R:
                    flag_changed = True
                    ChannelMode.set(A, ChannelModeEnum.R)

                if ChannelMode.get(B) != ChannelModeEnum.R:
                    flag_changed = True
                    ChannelMode.set(B, ChannelModeEnum.R)

                texture_shape_A = [M, K]
                texture_shape_B = [N, K]

            if TextureShape.get(A) != texture_shape_A:
                flag_changed = True
                TextureShape.set(A, height=texture_shape_A[0], width=texture_shape_A[1])

            if TextureShape.get(B) != texture_shape_B:
                flag_changed = True
                TextureShape.set(B, height=texture_shape_B[0], width=texture_shape_B[1])

        return graph, flag_changed
