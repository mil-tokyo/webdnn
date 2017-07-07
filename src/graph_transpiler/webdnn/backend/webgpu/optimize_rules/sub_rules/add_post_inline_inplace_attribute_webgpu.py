from typing import Tuple

from webdnn.backend.webgpu.attributes.inline_inject import PostInlineInplace
from webdnn.backend.webgpu.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.optimize_rule import OptimizeRule


class AddPostInlineInplaceAttribute(OptimizeRule):
    """
    PostInlineInplaceにカーネルが対応している場合、属性を付ける
    この属性はInjectInlineInplaceで使用される。
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        ops = traverse.listup_operators(graph)
        ops = traverse.filter_nodes(ops, PostInlineInplace, mode_not=True)
        for op in ops:  # type: Operator
            if isinstance(op, Sgemm):
                op.attributes.add(PostInlineInplace(op))
                flag_changed = True

            else:
                continue

        return graph, flag_changed
