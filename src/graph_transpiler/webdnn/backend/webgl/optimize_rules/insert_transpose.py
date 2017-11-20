from typing import Tuple, Union, List, Optional

from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
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
            if isinstance(op, (Tensordot,)):
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
                if all(axis in op.axes[0] for axis in C.order.axes[:A.ndim - len(op.axes[0])]):
                    # C's order is as [*a_remained_axes, *b_remained_axes], so it's not need to transpose C.
                    for i, axis in enumerate(C.order.axes[:A.ndim - len(op.axes[0])]):
                        a_axes.remove(axis)
                        a_axes.insert(i, axis)

                    for i, axis in enumerate(C.order.axes[A.ndim - len(op.axes[0]):]):
                        b_axes.remove(axis)
                        b_axes.insert(i, axis)

                else:
                    c_axes = a_axes[:(A.ndim - len(op.axes[0]))] + b_axes[:(B.ndim - len(op.axes[1]))]
                    flag_changed |= _replace_output(graph, op, "C", Order(c_axes))

                flag_changed |= _replace_input(graph, op, "A", Order(a_axes))
                flag_changed |= _replace_input(graph, op, "B", Order(b_axes))
                continue

            elif isinstance(op, (Im2Col,)):
                op = op  # type: Im2Col
                col = op.outputs["col"]

                # In variable "col", Axis.KH, Axis.KW, and Axis.C must be placed in this order.
                col_axes = list(col.order.axes)
                for axis in (Axis.KH, Axis.KW, Axis.C):
                    col_axes.remove(axis)
                    col_axes.append(axis)

                flag_changed |= _replace_output(graph, op, "col", Order(col_axes))
                continue

            elif isinstance(op, (Col2Im,)):
                op = op  # type: Col2Im
                col = op.inputs["col"]

                # In variable "col", Axis.KH, Axis.KW, and Axis.C must be placed in this order.
                col_axes = list(col.order.axes)
                for axis in (Axis.KH, Axis.KW, Axis.C):
                    col_axes.remove(axis)
                    col_axes.append(axis)

                flag_changed |= _replace_input(graph, op, "col", Order(col_axes))
                continue

            elif isinstance(op, (ConvertRGBAtoR, ConvertRtoRGBA)):
                flag_changed |= _replace_input(graph, op, "x0", op.outputs["y"].order)
                continue

            else:
                # "op" accepts any order. Remove redundant transpose operations if exist.
                for key in op.inputs:
                    flag_changed |= _optimize_redundant_transposed_input(graph, op, key, None)
                for key in op.outputs:
                    flag_changed |= _optimize_redundant_transposed_output(graph, op, key, None)
                continue

        return graph, flag_changed
