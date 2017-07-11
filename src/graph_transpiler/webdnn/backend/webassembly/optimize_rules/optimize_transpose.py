from typing import Tuple, Union, List

from webdnn.backend.webassembly.operators.im2col import Im2Col
from webdnn.backend.webassembly.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, OrderHWCN, OrderNC, OrderCN, Order, OrderCNHW
from webdnn.graph.traverse import dump
from webdnn.graph.variable import Variable


class OptimizeTranspose(OptimizeRule):
    """
    Insert transpose layer if needed.
    Currently, it is rule-based specific to each operator.
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        import sys
        sys.stderr.write("before optimizetranspose")
        dump(graph)
        flag_changed = False
        for op in traverse.listup_operators(graph):
            if isinstance(op, Reshape):
                flag_changed |= self._replace_input(op, "x", op.parameters["in_order"])
                flag_changed |= self._replace_output(op, "y", op.parameters["out_order"])
            elif isinstance(op, Convolution2D):
                flag_changed |= self._replace_input(op, "x", OrderNHWC)
                flag_changed |= self._replace_output(op, "y", OrderNHWC)

        sys.stderr.write("after optimizetranspose")
        dump(graph)
        return graph, flag_changed

    def _replace_input(self, op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
        orig_var = op.inputs[var_name]
        if isinstance(target_orders, Order):
            target_orders = [target_orders]
        if orig_var.order in target_orders:
            return False
        trans, = Transpose(None)(orig_var)
        trans.change_order(target_orders[0])
        op.remove_input(orig_var)
        op.append_input(var_name, trans)
        return True

    def _replace_output(self, op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
        orig_var = op.outputs[var_name]
        if isinstance(target_orders, Order):
            target_orders = [target_orders]
        if orig_var.order in target_orders:
            return False
        trans = Variable(orig_var.shape, orig_var.order)
        trans.change_order(target_orders[0])
        op.remove_output(orig_var)
        op.append_output(var_name, trans)
        transpose_op = Transpose(None)
        dummy_out, = transpose_op(trans)
        transpose_op.remove_output(dummy_out)
        transpose_op.append_output("y", orig_var)
        return True
