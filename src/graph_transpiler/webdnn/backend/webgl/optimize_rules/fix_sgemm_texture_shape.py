from typing import Tuple

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

            if transpose_A:
                if TextureShape.get(A) != [M, K]:
                    flag_changed = True
                    TextureShape.set(A, width=K, height=M)

            else:
                if TextureShape.get(A) != [K, M]:
                    flag_changed = True
                    TextureShape.set(A, width=M, height=K)

            if transpose_B:
                if TextureShape.get(B) != [K, N]:
                    flag_changed = True
                    TextureShape.set(B, width=N, height=K)

            else:
                if TextureShape.get(B) != [N, K]:
                    flag_changed = True
                    TextureShape.set(B, width=K, height=N)

        return graph, flag_changed
