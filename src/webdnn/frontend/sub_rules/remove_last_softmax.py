from typing import List

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util import flags


class RemoveLastSoftmax(OptimizeRule):
    """
    最終出力を作る関数がSoftmaxなら、これを削除する
    """

    def optimize(self, graph: Graph):
        if not flags.optimize.REMOVE_LAST_SOFTMAX:
            return graph, False

        flag_changed = False
        ops: List[Operator] = list(reversed(traverse.listup_operators(graph)))

        while len(ops) > 0:
            op = ops.pop(0)

            if isinstance(op, Softmax):
                op: Softmax

                x = op.inputs["x"]
                y = op.outputs["y"]
                op.remove_all()
                x.output_from.replace_output(x, y)

                flag_changed = True

            else:
                break

        return graph, flag_changed
