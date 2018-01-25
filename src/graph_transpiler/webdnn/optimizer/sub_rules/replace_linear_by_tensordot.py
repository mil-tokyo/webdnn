from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, OrderNC, Order


class ReplaceLinearByTensordot(OptimizeRule):
    """
    Replace Linear by Tensordot
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Linear):
            x = op.inputs["x"]
            w = op.inputs["w"]
            y = op.outputs["y"]

            flag_changed = True
            op.remove_all()
            a_filter = Axis()

            if x.ndim == 2:
                w, = ReinterpretAxis(None, in_order=OrderNC, out_order=Order([Axis.C, a_filter]))(w)
                new_y, = Tensordot(None, axes=[Axis.C, a_filter])(x, w)

            elif x.ndim == 4:
                w, = ReinterpretAxis(None, in_order=OrderNHWC, out_order=Order([Axis.C, Axis.H, Axis.W, a_filter]))(w)
                new_y, = Tensordot(None, axes=[[Axis.H, Axis.W, Axis.C], [Axis.H, Axis.W, a_filter]])(x, w)

            else:
                raise NotImplementedError

            OptimizeRule.replace_variable(graph, new_y.transpose_like(y), y)

        return graph, flag_changed
