from typing import Tuple, Union, List

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, Order, OrderNC
from webdnn.graph.variable import Variable


def _replace_input(op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
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


def _replace_output(op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
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


class OptimizeTranspose(OptimizeRule):
    """
    Insert transpose layer if needed.
    Currently, it is rule-based specific to each operator.
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.listup_operators(graph):
            if isinstance(op, Reshape):
                flag_changed |= _replace_input(op, "x", op.parameters["in_order"])
                flag_changed |= _replace_output(op, "y", op.parameters["out_order"])
            elif isinstance(op, (Convolution2D, MaxPooling2D, AveragePooling2D, Deconvolution2D)):
                flag_changed |= _replace_input(op, "x", OrderNHWC)
                flag_changed |= _replace_output(op, "y", OrderNHWC)
            elif isinstance(op, Softmax):
                x = op.inputs["x"]
                y = op.outputs["y"]

                if x.ndim > 2:
                    target_axis = op.parameters["axis"]
                    temp_axes_nd = x.order.axes
                    temp_axes_nd.remove(target_axis)
                    temp_axes_nd.append(target_axis)
                    temp_order_nd = Order(temp_axes_nd)
                    temp_shape_nd = [x.shape_dict[axis] for axis in temp_axes_nd]

                    temp_order_2d = OrderNC
                    temp_shape_2d = [x.size // x.shape_dict[target_axis], x.shape_dict[target_axis]]

                    flag_changed = True

                    hx, = Transpose(None)(x)
                    hx.change_order(temp_order_nd)
                    hx, = Reshape(None, in_order=hx.order, out_order=temp_order_2d,
                                  out_shape=temp_shape_2d)(hx)
                    op.remove_input(x)
                    op.append_input("x", hx)

                    hy = Variable(hx.shape, hx.order)
                    op.remove_output(y)
                    op.append_output("y", hy)
                    hy, = Reshape(None, in_order=temp_order_2d, out_order=temp_order_nd, out_shape=temp_shape_nd)(hy)
                    y_dummy, = Transpose(None)(hy)
                    y_dummy.replace(y)

                flag_changed |= _replace_input(op, "x", OrderNC)
                flag_changed |= _replace_output(op, "y", OrderNC)

        return graph, flag_changed
