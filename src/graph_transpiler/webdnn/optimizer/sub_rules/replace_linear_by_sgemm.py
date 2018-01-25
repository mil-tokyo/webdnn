from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.sgemm import Sgemm
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order


class ReplaceLinearBySgemm(OptimizeRule):
    """
    Replace Linear by Sgemm
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Linear):
            x = op.inputs["x"]
            w = op.inputs["w"]
            y = op.outputs["y"]

            flag_changed = True
            op.remove_all()

            a_k = Axis.C
            a_n = w.order.axes[0] if w.order.axes[1] == a_k else w.order.axes[1]
            axes_m = [a for a in x.order.axes if a != a_k]

            K = x.shape_dict[a_k]
            M = x.size // K
            N = w.shape_dict[a_n]

            x, = Transpose(None)(x)
            x.change_order(Order([a_k] + axes_m))

            w, = Transpose(None)(w)
            w.change_order(Order([a_k, a_n]))

            new_y, = Sgemm(None,
                           M=M, N=N, K=K,
                           out_shape=[x.shape_dict[a] for a in axes_m] + [N],
                           out_order=Order(axes_m + [a_n]),
                           transpose_A=False,
                           transpose_B=True)(x, w)
            new_y, = Transpose(None)(new_y)

            OptimizeRule.replace_variable(graph, new_y, y)

        return graph, flag_changed
