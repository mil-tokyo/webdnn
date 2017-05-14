from typing import Tuple

from graph_transpiler.backend.webgpu.attributes.inline_inject import PostInlineInplace
from graph_transpiler.backend.webgpu.operators.sgemm import Sgemm
from graph_transpiler.graph import traverse
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.operator import Operator
from graph_transpiler.graph.operators.elementwise_sum import ElementwiseSum
from graph_transpiler.graph.optimize_rule import OptimizeRule


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
            if isinstance(op, Sgemm) or isinstance(op, ElementwiseSum):
                op.attributes.add(PostInlineInplace(op))
                flag_changed = True

            else:
                continue

        return graph, flag_changed
