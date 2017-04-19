from typing import Tuple

from graph_builder.graph import Operator, operators as O
from graph_builder.graph.operators import attributes as A
from graph_builder.optimizer import OptimizeRule, util


class ConcatAxiswiseOperation(OptimizeRule):
    def __call__(self, graph: Operator):
        matches = util.search_sub_structure(graph, [
            A.Axiswise,
            A.PostAxiswise
        ])

        if len(matches) == 0:
            return graph, False

        for ops in matches:  # type: Tuple[Operator, Operator]
            composed = O.Compose.compose_ops("channelwise", ops)

            if not util.check_attribute_match(ops[0], A.PostAxiswise):
                composed.attributes.remove(A.PostAxiswise)

        return graph, True
