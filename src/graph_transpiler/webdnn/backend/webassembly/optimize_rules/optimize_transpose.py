from typing import Tuple

from webdnn.backend.webassembly.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, OrderHWCN, OrderNC, OrderCN
from webdnn.graph.variable import Variable


class OptimizeTranspose(OptimizeRule):
    """
    Insert transpose layer if needed.
    Currently, it is rule-based specific to each operator.
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.listup_operators(graph):
            if isinstance(op, Reshape):
                op: Reshape
                x = op.inputs["x"]
                y = op.outputs["y"]
                if x.order != op.parameters["in_order"]:
                    x_trans, = Transpose(None)(x)
                    x_trans.order = op.parameters["in_order"]
                    op.replace_input(x, x_trans)
                    flag_changed = True
                if y.order != op.parameters["out_order"]:
                    y_trans = Variable(y.shape, y.order)
                    y_trans.change_order(op.parameters["out_order"])
                    op.remove_output(y)
                    op.append_output("y", y_trans)
                    transpose_op = Transpose(None)
                    y_trans_out, = transpose_op(y_trans)
                    transpose_op.remove_output(y_trans_out)
                    transpose_op.append_output("y", y)
                    flag_changed = True

        return graph, flag_changed
