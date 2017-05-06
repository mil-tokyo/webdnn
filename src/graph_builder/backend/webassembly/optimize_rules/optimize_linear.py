from typing import Tuple

from graph_builder.backend.webassembly.operators.sgemm import Sgemm
from graph_builder.graph.axis import Axis
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.linear import Linear
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWCN, OrderNC, OrderCN
from graph_builder.optimize_rule import util
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class OptimizeLinear(OptimizeRule):
    """
    Linearをsgemmに置換する
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in util.listup_operators(graph):
            if not isinstance(op, Linear):
                continue

            op: Linear

            x = op.inputs["x"]
            w = op.inputs["w"]
            old_y = op.outputs["y"]
            assert x.axis_order == OrderNC or x.axis_order == OrderNHWC
            assert w.axis_order == OrderCN or w.axis_order == OrderHWCN
            assert old_y.axis_order == OrderNC or old_y.axis_order == OrderNHWC
            assert w.ndim == x.ndim

            flag_changed = True
            op.remove_all()

            sgemm = Sgemm(None,
                          M=old_y.shape_dict[Axis.N],
                          N=old_y.size // old_y.shape_dict[Axis.N],
                          K=x.size // x.shape_dict[Axis.N],
                          out_shape=old_y.shape,
                          out_order=old_y.axis_order,
                          transpose_A=True,
                          transpose_B=True)
            new_y, = sgemm(x, w)

            new_y.merge(old_y)

        return graph, flag_changed
