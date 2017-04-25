from typing import List

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.compose import Compose
from graph_builder.graph.operators.softmax import Softmax
from graph_builder.graph.variable import Variable
from graph_builder.optimize_rule.optimize_rule import OptimizeRule
from graph_builder.util import flags


class RemoveLastSoftmax(OptimizeRule):
    """
    最終出力を作る関数がSoftmaxなら、これを削除する
    """

    def optimize(self, graph: Operator):
        if not flags.optimize.REMOVE_LAST_SOFTMAX:
            return graph, False

        flag_changed = False
        var_queue: List[Variable] = list(graph.outputs.values())

        while len(var_queue) > 0:
            v = var_queue.pop(0)

            if isinstance(v.output_from, Compose):
                composed = v.output_from  # type: Compose
                var_queue.extend(list(composed.outputs_alias))
                continue

            elif isinstance(v.output_from, Softmax):
                softmax = v.output_from  # type: Softmax
                softmax.remove_self()
                flag_changed = True

        return graph, flag_changed
