from typing import Tuple

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.axiswise import Axiswise
from graph_builder.graph.operators.attributes.optimize_hint import AxiswiseOperationComposed
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.compose import Compose
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule


class ComposeAxiswiseOperation(OptimizeRule):
    def __call__(self, graph: Operator):
        matches = util.search_sub_structure(graph, [
            Axiswise,
            PostAxiswise
        ])

        if len(matches) == 0:
            return graph, False

        for ops in matches:  # type: Tuple[Operator, Operator]
            composed = Compose.compose_ops("channelwise", ops)
            composed.attributes.add(AxiswiseOperationComposed)

            if not util.check_attribute_match(ops[0], PostAxiswise):
                composed.attributes.remove(PostAxiswise)

        return graph, True
