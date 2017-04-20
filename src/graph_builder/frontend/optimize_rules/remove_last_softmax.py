from typing import List

from graph_builder.graph import Operator, operators as O, Variable
from graph_builder.optimizer import OptimizeRule
from graph_builder.util import flags


class RemoveLastSoftmax(OptimizeRule):
    """
    最終出力を作る関数がSoftmaxなら、これを削除する
    """

    def __call__(self, graph: Operator):
        if not flags.optimize.REMOVE_LAST_SOFTMAX:
            return graph, False

        flag_changed = False
        var_queue: List[Variable] = list(graph.outputs.values())

        while len(var_queue) > 0:
            v = var_queue.pop(0)

            if isinstance(v.output_from, O.Compose):
                composed = v.output_from  # type: O.Compose
                var_queue.extend(list(composed.outputs_alias))
                continue

            elif isinstance(v.output_from, O.Softmax):
                softmax = v.output_from  # type: O.Softmax
                softmax.remove_self()
                flag_changed = True

        return graph, flag_changed
