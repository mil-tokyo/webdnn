from typing import Tuple

from graph_builder.graph import Operator, operators as O
from graph_builder.graph.operators import attributes as A
from graph_builder.optimizer import OptimizeRule
from graph_builder.util import flags


class ConcatElementwiseOperation(OptimizeRule):
    # noinspection PyMethodMayBeStatic
    def is_enabled(self):
        return flags.optimize.CONCAT_ELEMENTWISE_OPERATION

    def optimize(self, graph: Operator) -> Operator:
        matches = self.optimizer.search_sub_structure([
            A.Elementwise,
            A.PostElementwise
        ])

        for ops in matches:  # type: Tuple[Operator, Operator]
            composed = O.Compose.compose_ops("channelwise", ops)

            # これは正しいのか?
            composed.attributes.update(ops[0].attributes)
            composed.attributes.update(ops[1].attributes)

        return graph
