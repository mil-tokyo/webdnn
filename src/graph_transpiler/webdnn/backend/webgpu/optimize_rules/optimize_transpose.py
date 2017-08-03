from typing import Tuple, Union, List

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.split_axis import SplitAxis
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
            if isinstance(op, Transpose):
                x = op.inputs["x0"]
                y = op.outputs["y"]
                if x.order == y.order:
                    op.remove_all()
                    x.replace(y)
                    flag_changed = True

                if all(isinstance(op2, (Elementwise, SplitAxis)) for op2 in y.input_to):
                    op.remove_all()
                    for op2 in list(y.input_to):
                        name = op2._get_input_name(y)
                        op2.remove_input(y)
                        op2.append_input(name, x)

            elif isinstance(op, Reshape):
                flag_changed |= _replace_input(op, "x", op.parameters["in_order"])
                flag_changed |= _replace_output(op, "y", op.parameters["out_order"])

            elif isinstance(op, (Convolution2D, MaxPooling2D, AveragePooling2D, Deconvolution2D)):
                flag_changed |= _replace_input(op, "x", OrderNHWC)
                flag_changed |= _replace_output(op, "y", OrderNHWC)

            elif isinstance(op, Softmax):
                x = op.inputs["x"]
                y = op.outputs["y"]

                if x.ndim > 2:
                    """
                    Before)
                    | x    |              | y    |
                    |------| -{softmax}-> |------|
                    | NCHW |              | NCHW |
                    
                    After)
                    | x    |                | hx1  |              | hx2 |              | hy1 |              | hy2  |                | y    |
                    |------| -{transpose}-> |------| -{reshape}-> |-----| -{softmax}-> |-----| -{reshape}-> |------| -{transpose}-> |------|
                    | NCHW |                | NHWC |              | NC  |              | NC  |              | NHWC |                | NCHW |
                    """
                    op.remove_all()

                    target_axis = op.parameters["axis"]
                    axes_nd = list(x.order.axes)
                    axes_nd.remove(target_axis)
                    axes_nd.append(target_axis)
                    order_nd = Order(axes_nd)
                    shape_nd = [x.shape_dict[axis] for axis in axes_nd]

                    order_2d = OrderNC
                    shape_2d = [x.size // x.shape_dict[target_axis], x.shape_dict[target_axis]]

                    hx1, = Transpose(None)(x)
                    hx1.change_order(order_nd)

                    hx2, = Reshape(None, in_order=hx1.order, out_order=order_2d, out_shape=shape_2d)(hx1)

                    hy1, = Softmax(None, axis=Axis.C)(hx2)

                    hy2, = Reshape(None, in_order=hy1.order, out_order=order_nd, out_shape=shape_nd)(hy1)

                    y_dummy, = Transpose(None)(hy2)
                    y_dummy.change_order(y.order)

                    y_dummy.replace(y)
                    flag_changed = True

                else:
                    flag_changed |= _replace_input(op, "x", OrderNC)
                    flag_changed |= _replace_output(op, "y", OrderNC)

        return graph, flag_changed
