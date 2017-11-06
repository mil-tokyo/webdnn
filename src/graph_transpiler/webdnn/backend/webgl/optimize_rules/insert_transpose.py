from typing import Tuple, Union, List

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.unpooling_2d import Unpooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.space2depth import Space2Depth
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC, Order
from webdnn.graph.variable import Variable


def _replace_input(op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
    v = op.inputs[var_name]

    if isinstance(target_orders, Order):
        target_orders = [target_orders]
    if v.order in target_orders:
        return False

    v_new, = Transpose(None)(v)
    op.replace_input(v, v_new, with_assert=False)
    v_new.change_order(target_orders[0])
    return True


def _replace_output(op: Operator, var_name: str, target_orders: Union[Order, List[Order]]):
    v = op.outputs[var_name]

    if isinstance(target_orders, Order):
        target_orders = [target_orders]
    if v.order in target_orders:
        return False

    v_new = Variable(v.shape, v.order).change_order(target_orders[0])
    op.replace_output(v, v_new, with_assert=False)
    Transpose(None)(v_new)[0].replace(v, with_assert=False)
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
                    x.replace(y)

                    if x in graph.inputs:
                        index = graph.inputs.index(x)
                        graph.inputs.remove(x)
                        graph.inputs.insert(index, y)

                    flag_changed = True
                    continue

                if y not in graph.outputs and all(isinstance(op2, (Elementwise, SplitAxis)) for op2 in y.input_to):
                    """
                    before)

                        x-[Transpose]-y-[Elementwise]-

                    after)

                        x-[Elementwise]-
                    """
                    op.remove_all()
                    for op2 in list(y.input_to):
                        op2.replace_input(y, x, with_assert=False)

                    flag_changed = True
                    continue

                if y not in graph.outputs and isinstance(x.output_from, (Elementwise, SplitAxis)):
                    """
                    before)
                    
                        -[Elementwise]-x-[Transpose]-y-
                    
                    after)
                    
                        -[Elementwise]-x-
                    """
                    op.remove_all()
                    y.replace(x, with_assert=False)
                    x.change_order(y.order)
                    flag_changed = True
                    continue

            elif isinstance(op, Reshape):
                flag_changed |= _replace_input(op, "x", op.parameters["in_order"])
                flag_changed |= _replace_output(op, "y", op.parameters["out_order"])
                continue

            elif isinstance(op, Im2Col):
                flag_changed |= _replace_input(op, "im", OrderNHWC)
                flag_changed |= _replace_output(op, "col", OrderNHWC)
                continue

            elif isinstance(op, Col2Im):
                flag_changed |= _replace_input(op, "col", OrderNHWC)
                flag_changed |= _replace_output(op, "im", OrderNHWC)
                continue

            elif isinstance(op, (Convolution2D, Deconvolution2D, MaxPooling2D, AveragePooling2D, Space2Depth, Depth2Space, Unpooling2D)):
                flag_changed |= _replace_input(op, "x", OrderNHWC)
                flag_changed |= _replace_output(op, "y", OrderNHWC)
                continue

        return graph, flag_changed
