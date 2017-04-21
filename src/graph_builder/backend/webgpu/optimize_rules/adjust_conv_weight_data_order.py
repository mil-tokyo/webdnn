from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.variables.attributes.order import OrderHWCN
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule


class AdjustConvWeightDataOrder(OptimizeRule):
    """
    Convolution2DのフィルタをHWCNオーダーに揃える
    """

    def __call__(self, graph: Operator):
        flag_changed = False
        for op in util.listup_operator_in_order(graph):
            if not isinstance(op, Convolution2D):
                continue

            op: Convolution2D

            w = op.inputs["w"]  # type: ConstantVariable
            if w.axis_order == OrderHWCN:
                continue

            flag_changed = True
            w.change_axis_order(OrderHWCN)

        return graph, flag_changed
