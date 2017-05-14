from typing import Tuple

from graph_transpiler.backend.webgpu.attributes.inline_inject import InlineInplace, PostInlineInplace
from graph_transpiler.graph import traverse
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.optimize_rule import OptimizeRule
from graph_transpiler.graph.variable import Variable
from graph_transpiler.util import flags


class InjectInlineInplace(OptimizeRule):
    """
    PostInlineInplaceへInlineInplaceを注入する
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not flags.optimize.INJECT_INLINE_INPLACE:
            return graph, False

        matches = traverse.search_sub_structure(graph, [PostInlineInplace, Variable, InlineInplace])
        flag_changed = False

        for match in matches:
            op1 = match[0]
            op2 = match[2]
            post_inline_inplace = op1.get_attribute(PostInlineInplace)[0]  # type: PostInlineInplace
            inline_inplace = op2.get_attribute(InlineInplace)[0]  # type: InlineInplace

            x = inline_inplace.get_input()
            y = inline_inplace.get_output()

            if len(x.input_to) > 1:
                continue

            op2.remove_all()
            op1.replace_output(x, y)
            post_inline_inplace.register_injected(inline_inplace)
            flag_changed = True

        return graph, flag_changed
