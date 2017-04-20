from typing import Tuple

from graph_builder.graph import Operator, operators as O
from graph_builder.graph.operators import attributes as A
from graph_builder.optimizer import OptimizeRule, util


class ComposeElementwiseOperation(OptimizeRule):
    def __call__(self, graph: Operator):
        matches = util.search_sub_structure(graph, [
            A.Elementwise,
            A.PostElementwise
        ])

        if len(matches) == 0:
            return graph, False

        for ops in matches:  # type: Tuple[Operator, Operator]
            composed = O.Compose.compose_ops("channelwise", ops)
            composed.attributes.add(A.ElementwiseOperationComposed)

            if not util.check_attribute_match(ops[0], A.PostElementwise):
                composed.attributes.remove(A.PostElementwise)

        return graph, True
