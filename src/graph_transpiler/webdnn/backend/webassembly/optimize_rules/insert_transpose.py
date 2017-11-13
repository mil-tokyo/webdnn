from typing import Tuple, Union, List

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.space2depth import Space2Depth
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.operators.unpooling_2d import Unpooling2D
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, Order, OrderNC
from webdnn.graph.variable import Variable


def _replace_input(op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
    v = op.inputs[var_name]

    if isinstance(target_orders, Order):
        target_orders = [target_orders]
    if v.order in target_orders:
        return False

    op.replace_input(v, v.transpose(target_orders[0]), with_assert=False)
    return True


def _replace_output(op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
    v = op.outputs[var_name]

    if isinstance(target_orders, Order):
        target_orders = [target_orders]
    if v.order in target_orders:
        return False

    v_new = Variable(v.shape, v.order).change_order(target_orders[0])
    op.replace_output(v, v_new, with_assert=False)
    v_new.transpose(v.order).replace(v, with_assert=False)
    return True


class InsertTranspose(OptimizeRule):
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
                    OptimizeRule.replace_variable(graph, x, y)

                    if x in graph.inputs:
                        index = graph.inputs.index(x)
                        graph.inputs.remove(x)
                        graph.inputs.insert(index, y)

                    flag_changed = True
                    continue

                if y not in graph.outputs and all(isinstance(op2, (Elementwise, SplitAxis)) for op2 in y.input_to):
                    op.remove_all()
                    for op2 in list(y.input_to):
                        name = op2.get_input_name(y)
                        op2.remove_input(y)
                        op2.append_input(name, x)

                    flag_changed = True
                    continue

            elif isinstance(op, Reshape):
                flag_changed |= _replace_input(op, "x", op.parameters["in_order"])
                flag_changed |= _replace_output(op, "y", op.parameters["out_order"])
                continue

            elif isinstance(op, (Tensordot,)):
                op = op  # type: Tensordot
                A = op.inputs["A"]
                B = op.inputs["B"]
                C = op.outputs["C"]

                # Reduced axes must be located in inner side.
                a_axes = list(A.order.axes)
                for axis in op.axes[0]:
                    a_axes.remove(axis)
                    a_axes.append(axis)

                b_axes = list(B.order.axes)
                for axis in op.axes[1]:
                    b_axes.remove(axis)
                    b_axes.append(axis)

                # Remained axes must be located in same order as A and B's axes order.
                if all(axis in a_axes for axis in C.order.axes[:A.ndim - len(op.axes[0])]):
                    # C's order is as [*a_remained_axes, *b_remained_axes], so it's not need to transpose C.
                    for i, axis in enumerate(C.order.axes[:A.ndim - len(op.axes[0])]):
                        a_axes.remove(axis)
                        a_axes.insert(i, axis)

                    for i, axis in enumerate(C.order.axes[A.ndim - len(op.axes[0]):]):
                        b_axes.remove(axis)
                        b_axes.insert(i, axis)

                else:
                    c_axes = a_axes[:len(op.axes[0])] + b_axes[:len(op.axes[1])]
                    flag_changed |= _replace_output(op, "C", Order(c_axes))

                flag_changed |= _replace_input(op, "A", Order(a_axes))
                flag_changed |= _replace_input(op, "B", Order(b_axes))
                continue

            elif isinstance(op, (Convolution2D, Deconvolution2D,
                                 MaxPooling2D, AveragePooling2D,
                                 Space2Depth, Depth2Space,
                                 LocalResponseNormalization,
                                 Unpooling2D)):
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
                        hx1 = x.transpose(order_nd)
                        flag_changed = True

                    if hx1.order == order_2d and hx1.shape == shape_2d:
                        hx2 = hx1

                    else:
                        hx2 = hx1.reshape(shape_2d, order_2d)
                        flag_changed = True

                    hy1, = Softmax(None, axis=Axis.C)(hx2)

                    if hy1.order == order_nd and hy1.shape == shape_nd:
                        hy2 = hy1

                    else:
                        hy2 = hy1.reshape(shape_nd, order_nd)
                        flag_changed = True

                    if hy2.order == y.order:
                        y_dummy = hy2

                    else:
                        y_dummy = hy2.transpose(y.order)
                        flag_changed = True

                    OptimizeRule.replace_variable(graph, y_dummy, y)

                    continue

        return graph, flag_changed
