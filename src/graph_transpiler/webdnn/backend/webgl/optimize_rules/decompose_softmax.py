from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.exp import Exp
from webdnn.graph.operators.max import Max
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.sum import Sum
from webdnn.graph.optimize_rule import OptimizeRule


class DecomposeSoftmax(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for softmax in traverse.filter_nodes(traverse.listup_operators(graph), Softmax):
            x = softmax.inputs["x"]
            y = softmax.outputs["y"]
            axis = softmax.parameters["axis"]
            softmax.remove_all()
            flag_changed = True

            max_x, = Max(None, axis=axis)(x)
            delta_x = x - max_x
            exp_delta_x, = Exp(None)(delta_x)
            sum_exp_delta_x, = Sum(None, axis=axis)(exp_delta_x)
            new_y = exp_delta_x / sum_exp_delta_x

            new_y.change_order(y.order)
            OptimizeRule.replace_variable(graph, new_y, y)

        return graph, flag_changed
