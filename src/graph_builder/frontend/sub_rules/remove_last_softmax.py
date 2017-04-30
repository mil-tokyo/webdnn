from typing import List

from graph_builder.graph.graph import Graph
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.softmax import Softmax
from graph_builder.optimize_rule import util
from graph_builder.optimize_rule.optimize_rule import OptimizeRule
from graph_builder.util import flags


class RemoveLastSoftmax(OptimizeRule):
    """
    最終出力を作る関数がSoftmaxなら、これを削除する
    """

    def optimize(self, graph: Graph):
        if not flags.optimize.REMOVE_LAST_SOFTMAX:
            return graph, False

        flag_changed = False
        ops: List[Operator] = reversed(util.listup_operators(graph))

        while len(ops) > 0:
            op = ops.pop(0)

            if isinstance(op, Softmax):
                op: Softmax
                x = op.inputs["x"]
                y = op.outputs["y"]
                op.remove_self()
                x.merge(y)
                flag_changed = True

            else:
                break

        return graph, flag_changed
