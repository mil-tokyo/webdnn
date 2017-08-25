from typing import Tuple, Union, List

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.space2depth import Space2Depth
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
                continue

            elif isinstance(op, (Convolution2D, Deconvolution2D,
                                 MaxPooling2D, AveragePooling2D,
                                 Space2Depth, Depth2Space,
                                 LocalResponseNormalization)):
                flag_changed |= _replace_input(op, "x", OrderNHWC)
                flag_changed |= _replace_output(op, "y", OrderNHWC)
                continue

            elif isinstance(op, Softmax):
                x = op.inputs["x"]
                y = op.outputs["y"]
                target_axis = op.parameters["axis"]

                if not (x.ndim == 2 and x.order.axes_dict[target_axis] == x.ndim - 1):
                    """
                    Before)
                    | x   |              | y   |
                    |-----| -{softmax}-> |-----|
                    | XYZ |   axis=Y     | XYZ |
                    
                    After)
                    | x   |                | hx1 |              | hx2 |              | hy1 |              | hy2 |                | y   |
                    |-----| -{transpose}-> |-----| -{reshape}-> |-----| -{softmax}-> |-----| -{reshape}-> |-----| -{transpose}-> |-----|
                    | XYZ |                | XZY |              | NC  |   axis=C     | NC  |              | XZY |                | XYZ |
                                              :                    :
                                        order_nd = XZY       order_2d = NC
                    """
                    op.remove_all()

                    axes_nd = list(x.order.axes)
                    axes_nd.remove(target_axis)
                    axes_nd.append(target_axis)
                    order_nd = Order(axes_nd)
                    shape_nd = tuple([x.shape_dict[axis] for axis in axes_nd])

                    order_2d = OrderNC
                    shape_2d = tuple([x.size // x.shape_dict[target_axis], x.shape_dict[target_axis]])

                    if x.order == order_nd:
                        hx1 = x

                    else:
                        hx1, = Transpose(None)(x)
                        hx1.change_order(order_nd)
                        flag_changed = True

                    if hx1.order == order_2d and hx1.shape == shape_2d:
                        hx2 = hx1

                    else:
                        hx2, = Reshape(None, in_order=hx1.order, out_order=order_2d, out_shape=shape_2d)(hx1)
                        flag_changed = True

                    hy1, = Softmax(None, axis=Axis.C)(hx2)

                    if hy1.order == order_nd and hy1.shape == shape_nd:
                        hy2 = hy1

                    else:
                        hy2, = Reshape(None, in_order=hy1.order, out_order=order_nd, out_shape=shape_nd)(hy1)
                        flag_changed = True

                    if hy2.order == y.order:
                        y_dummy = hy2

                    else:
                        y_dummy, = Transpose(None)(hy2)
                        y_dummy.change_order(y.order)
                        flag_changed = True

                    y_dummy.replace(y)

                    continue

        return graph, flag_changed
