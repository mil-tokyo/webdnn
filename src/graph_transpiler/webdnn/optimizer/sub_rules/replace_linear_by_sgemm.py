from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.sgemm import Sgemm
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, OrderHWCN, OrderNC, OrderCN


class ReplaceLinearBySgemm(OptimizeRule):
    """
    Replace Linear by Sgemm
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Linear):  # type: Linear
            x = op.inputs["x"]
            w = op.inputs["w"]
            y = op.outputs["y"]

            flag_changed = True
            op.remove_all()

            if x.ndim == 2:
                x = x.transpose(OrderNC)
                w = w.transpose(OrderCN)

            elif x.ndim == 4:
                x = x.transpose(OrderNHWC)
                w = w.transpose(OrderHWCN)

            else:
                raise NotImplementedError

            new_y, = Sgemm(None,
                           M=y.shape_dict[Axis.N],
                           N=y.size // y.shape_dict[Axis.N],
                           K=x.size // x.shape_dict[Axis.N],
                           out_shape=[y.shape_dict[Axis.N], y.size // y.shape_dict[Axis.N]],
                           out_order=OrderNC,
                           transpose_A=True,
                           transpose_B=True)(x, w)

            OptimizeRule.replace_variable(graph, new_y.transpose_like(y), y)

        return graph, flag_changed
