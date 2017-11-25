from typing import Tuple, Union, List, Optional

from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.space2depth import Space2Depth
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.operators.unpooling_2d import Unpooling2D
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, Order, OrderNT, OrderCN, OrderNTC, OrderNC
from webdnn.graph.variable import Variable


def _replace_input(graph: Graph, op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
    v = op.inputs[var_name]

    if isinstance(target_orders, Order):
        target_orders = [target_orders]

    if v.order in target_orders:
        return _optimize_redundant_transposed_input(graph, op, var_name, target_orders)

    op.replace_input(v, v.transpose(target_orders[0]), with_assert=False)
    return True


def _optimize_redundant_transposed_input(graph: Graph, op: Operator, var_name: str,
                                         target_orders: Optional[Union[Order, List[Order]]] = None):
    v = op.inputs[var_name]
    op2 = v.output_from

    if len(v.input_to) != 1 or not isinstance(op2, Transpose):
        return False

    if target_orders is not None:
        if isinstance(target_orders, Order):
            target_orders = [target_orders]

        if op2.inputs["x0"].order not in target_orders:
            return False

    v2 = op2.inputs["x0"]
    op2.remove_all()
    OptimizeRule.replace_variable(graph, v, v2, with_assert=False)
    return True


def _replace_output(graph: Graph, op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
    v = op.outputs[var_name]

    if isinstance(target_orders, Order):
        target_orders = [target_orders]

    if v.order in target_orders:
        return _optimize_redundant_transposed_output(graph, op, var_name, target_orders)

    v_new = Variable(v.shape, v.order).change_order(target_orders[0])
    op.replace_output(v, v_new, with_assert=False)
    v_new.transpose(v.order).replace(v, with_assert=False)
    return True


def _optimize_redundant_transposed_output(graph: Graph, op: Operator, var_name: str,
                                          target_orders: Optional[Union[Order, List[Order]]] = None):
    v = op.outputs[var_name]

    if len(v.input_to) != 1:
        return False

    op2 = list(v.input_to)[0]

    if not isinstance(op2, Transpose):
        return False

    if target_orders is not None:
        if isinstance(target_orders, Order):
            target_orders = [target_orders]

        if op2.outputs["y"].order not in target_orders:
            return False

    v2 = op2.outputs["y"]
    op2.remove_all()
    OptimizeRule.replace_variable(graph, v, v2, with_assert=False)
    return True


class InsertTranspose(OptimizeRule):
    """
    Insert transpose layer if needed.
    Currently, it is rule-based specific to each operator.
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.listup_operators(graph):
            if isinstance(op, (Reshape, ReinterpretAxis)):
                flag_changed |= _replace_input(graph, op, "x", op.parameters["in_order"])
                flag_changed |= _replace_output(graph, op, "y", op.parameters["out_order"])
                continue

            elif isinstance(op, LSTM):
                flag_changed |= _replace_input(graph, op, "x", OrderNTC)
                if "w_all" in op.inputs:
                    flag_changed |= _replace_input(graph, op, "w_all", OrderCN)
                else:
                    flag_changed |= _replace_input(graph, op, "w_input", OrderCN)
                    flag_changed |= _replace_input(graph, op, "w_hidden", OrderCN)
                flag_changed |= _replace_output(graph, op, "y", OrderNTC if op.parameters["return_sequences"] else OrderNC)
                flag_changed |= _replace_output(graph, op, "final_c", OrderNC)
                continue

            elif isinstance(op, Embedding):
                flag_changed |= _replace_input(graph, op, "x", OrderNT)
                flag_changed |= _replace_input(graph, op, "w", OrderCN)
                flag_changed |= _replace_output(graph, op, "y", OrderNTC)
                continue

            elif isinstance(op, Im2Col):
                flag_changed |= _replace_input(graph, op, "im", OrderNHWC)
                flag_changed |= _replace_output(graph, op, "col", [Order([Axis.KH, Axis.KW, Axis.C, Axis.N, Axis.H, Axis.W]),
                                                                   Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C])])
                continue

            elif isinstance(op, Col2Im):
                flag_changed |= _replace_input(graph, op, "col", [Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C])])
                flag_changed |= _replace_output(graph, op, "im", OrderNHWC)
                continue

            elif isinstance(op, (Tensordot,)):
                op = op  # type: Tensordot
                A = op.inputs["A"]
                B = op.inputs["B"]
                C = op.outputs["C"]

                # Reduced axes must be located in out side.
                a_axes = list(A.order.axes)
                for i, axis in enumerate(op.axes[0]):
                    a_axes.remove(axis)
                    a_axes.insert(i, axis)

                b_axes = list(B.order.axes)
                for i, axis in enumerate(op.axes[1]):
                    b_axes.remove(axis)
                    b_axes.insert(i, axis)

                # Remained axes must be located in same order as A and B's axes order.
                if all(axis in op.axes[0] for axis in C.order.axes[:A.ndim - len(op.axes[0])]):
                    # C's order is as [*a_remained_axes, *b_remained_axes], so it's not need to transpose C.
                    for axis in C.order.axes[:A.ndim - len(op.axes[0])]:
                        a_axes.remove(axis)
                        a_axes.append(axis)

                    for axis in C.order.axes[A.ndim - len(op.axes[0]):]:
                        b_axes.remove(axis)
                        b_axes.append(axis)

                else:
                    c_axes = a_axes[len(op.axes[0]):] + b_axes[len(op.axes[1]):]
                    flag_changed |= _replace_output(graph, op, "C", Order(c_axes))

                flag_changed |= _replace_input(graph, op, "A", Order(a_axes))
                flag_changed |= _replace_input(graph, op, "B", Order(b_axes))
                continue

            elif isinstance(op, (Convolution2D, Deconvolution2D,
                                 MaxPooling2D, AveragePooling2D,
                                 Space2Depth, Depth2Space,
                                 LocalResponseNormalization,
                                 Unpooling2D)):
                flag_changed |= _replace_input(graph, op, "x", OrderNHWC)
                flag_changed |= _replace_output(graph, op, "y", OrderNHWC)
                continue

            elif isinstance(op, Softmax):
                flag_changed |= _replace_output(graph, op, "y", op.inputs["x"].order)
                continue

            else:
                # "op" accepts any order. Remove redundant transpose operations if exist.
                for key in op.inputs:
                    flag_changed |= _optimize_redundant_transposed_input(graph, op, key, None)
                for key in op.outputs:
                    flag_changed |= _optimize_redundant_transposed_output(graph, op, key, None)
                continue

        return graph, flag_changed
