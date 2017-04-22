from typing import Tuple

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.elementwise import Elementwise
from graph_builder.graph.operators.attributes.optimize_hint import ElementwiseOperationComposed
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.operators.compose import Compose
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule


class ComposeElementwiseOperation(OptimizeRule):
    def __call__(self, graph: Operator):
        matches = util.search_sub_structure(graph, [
            PostElementwise,
            Elementwise
        ])

        if len(matches) == 0:
            return graph, False

        for ops in matches:  # type: Tuple[Operator, Operator]
            composed = Compose.compose_ops("channelwise", ops)
            composed.attributes.add(ElementwiseOperationComposed)

            if not util.check_attribute_match(ops[0], Elementwise):
                composed.attributes.remove(Elementwise)

        return graph, True
