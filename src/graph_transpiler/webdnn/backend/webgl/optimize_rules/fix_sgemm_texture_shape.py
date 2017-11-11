from typing import Tuple

from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.sgemm import Sgemm
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
from webdnn.graph.variables.constant_variable import ConstantVariable


class FixSGEMMTextureShape(OptimizeRule):
    def __init__(self, optimize_channel_mode: bool = False):
        super(FixSGEMMTextureShape, self).__init__()
        self.optimize_channel_mode = optimize_channel_mode

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for sgemm in traverse.filter_nodes(traverse.listup_operators(graph), Sgemm):  # type: Sgemm
            A = sgemm.inputs["A"]
            B = sgemm.inputs["B"]
            M = sgemm.M
            N = sgemm.N
            K = sgemm.K
            transpose_A = sgemm.transpose_A
            transpose_B = sgemm.transpose_B

            if all([self.optimize_channel_mode,
                    K % 4 == 0,
                    isinstance(A, ConstantVariable) or transpose_A == True,
                    isinstance(B, ConstantVariable) or transpose_B == False]):
                if transpose_A != True:
                    assert isinstance(A, ConstantVariable)
                    flag_changed = True
                    old_A = A
                    A = ConstantVariable(A.data.reshape([K, M]).transpose(), Order([Axis(None), Axis(None)]))
                    ChannelMode.set(A, ChannelMode.get(old_A))
                    sgemm.replace_input(old_A, A, with_assert=False)
                    sgemm.parameters["transpose_A"] = transpose_A = True

                if transpose_B != False:
                    assert isinstance(B, ConstantVariable)
                    flag_changed = True
                    old_B = B
                    B = ConstantVariable(B.data.reshape([K, N]).transpose(), Order([Axis(None), Axis(None)]))
                    ChannelMode.set(B, ChannelMode.get(old_B))
                    sgemm.replace_input(old_B, B, with_assert=False)
                    sgemm.parameters["transpose_B"] = transpose_B = False

                if ChannelMode.get(A) != ChannelModeEnum.RGBA:
                    flag_changed = True
                    ChannelMode.set(A, ChannelModeEnum.RGBA)

                if ChannelMode.get(B) != ChannelModeEnum.RGBA:
                    flag_changed = True
                    ChannelMode.set(B, ChannelModeEnum.RGBA)

                texture_shape_A = [M, K // 4] if transpose_A else [K // 4, M]
                texture_shape_B = [K // 4, N] if transpose_B else [N, K // 4]

            else:
                if ChannelMode.get(A) != ChannelModeEnum.R:
                    flag_changed = True
                    ChannelMode.set(A, ChannelModeEnum.R)

                if ChannelMode.get(B) != ChannelModeEnum.R:
                    flag_changed = True
                    ChannelMode.set(B, ChannelModeEnum.R)

                texture_shape_A = [M, K] if transpose_A else [K, M]
                texture_shape_B = [K, N] if transpose_B else [N, K]

            if TextureShape.get(A) != texture_shape_A:
                flag_changed = True
                TextureShape.set(A, height=texture_shape_A[0], width=texture_shape_A[1])

            if TextureShape.get(B) != texture_shape_B:
                flag_changed = True
                TextureShape.set(B, height=texture_shape_B[0], width=texture_shape_B[1])

        return graph, flag_changed
