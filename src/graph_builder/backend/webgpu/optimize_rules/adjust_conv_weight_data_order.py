from graph_builder.graph import Operator, operators as O
from graph_builder.graph.variables import attributes as VA, Constant
from graph_builder.optimizer import OptimizeRule, util


class AdjustConvWeightDataOrder(OptimizeRule):
    """
    Convolution2DのフィルタをHWCNオーダーに揃える
    """

    def __call__(self, graph: Operator):
        flag_changed = False
        for op in util.listup_operator_in_order(graph):
            if not isinstance(op, O.Convolution2D):
                continue

            conv = op  # type: O.Convolution2D

            w = conv.inputs["w"]  # type: Constant
            if w.axis_order == VA.OrderHWCN:
                continue

            flag_changed = True
            w.change_axis_order(VA.OrderHWCN)

        return graph, flag_changed
