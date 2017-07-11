from typing import Tuple

from webdnn.backend.code_generator.injectors.inline_injector import InlineInplace
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.optimize_rule import OptimizeRule


class AddInlineInplaceAttribute(OptimizeRule):
    """
    InlineInplaceにカーネルが対応している場合、属性を付ける
    この属性はInjectInlineInplaceで使用される。
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        ops = traverse.listup_operators(graph)
        ops = traverse.filter_nodes(ops, Inplace)
        ops = traverse.filter_nodes(ops, InlineInplace, mode_not=True)
        for op in ops:  # type: Operator
            inplace = op.get_attribute(Inplace)[0]  # type: Inplace

            if isinstance(op, Relu):
                op.attributes.add(InlineInplace(op, lambda exp: f"({exp}>0?{exp}:0)", inplace))
                flag_changed = True

            elif isinstance(op, Elu):
                op.attributes.add(InlineInplace(op, lambda exp: f"({exp}>0?{exp}:(exp({exp})-1))", inplace))
                flag_changed = True

            elif isinstance(op, Tanh):
                op.attributes.add(InlineInplace(op, lambda exp: f"(tanh({exp}))", inplace))
                flag_changed = True

            else:
                continue

        return graph, flag_changed
