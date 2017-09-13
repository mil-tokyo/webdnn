from typing import Tuple

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.backend.webgl.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.optimize_rule import OptimizeRule


class FixSGEMMTextureShape(OptimizeRule):
    """
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Sgemm):  # type: Sgemm
            A = op.inputs["A"]
            B = op.inputs["B"]
            M = op.M
            N = op.N
            K = op.K
            transpose_A = op.transpose_A
            transpose_B = op.transpose_B

            K_A = K // ChannelMode.elements_per_pixel(A)
            shape_A = [M, K_A] if transpose_A else [K_A, M]
            if TextureShape.get(A) != shape_A:
                flag_changed = True
                TextureShape.set(A, height=shape_A[0], width=shape_A[1])

            K_B = K // ChannelMode.elements_per_pixel(B)
            shape_B = [K_B, N] if transpose_B else [N, K_B]
            if TextureShape.get(B) != shape_B:
                flag_changed = True
                TextureShape.set(B, height=shape_B[0], width=shape_B[1])

        return graph, flag_changed
