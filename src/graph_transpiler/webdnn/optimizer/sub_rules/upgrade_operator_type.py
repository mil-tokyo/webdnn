from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util import flags, console


class UpgradeOperatorType(OptimizeRule):
    """
    Upgrade operator type which is deprecated to new operator type.
    """

    def flags(self):
        return [
            flags.AUTO_UPGRADE_OPERATOR_TYPE
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        # replace AxiswiseBias by ElementwiseAdd
        flag_warn = True
        for op in traverse.filter_nodes(traverse.listup_operators(graph), AxiswiseBias):
            flag_changed = True
            x = op.inputs["x0"]
            b = op.inputs["x1"]
            y = op.outputs["y"]
            op.remove_all()
            OptimizeRule.replace_variable(graph, (x + b).change_order(y.order), y)

            if flag_warn:
                flag_warn = False
                console.warning("AxiswiseBias will be removed in the future version. Use ElementwiseAdd.", DeprecationWarning)

        # replace AxiswiseScale by ElementwiseMul
        flag_warn = True
        for op in traverse.filter_nodes(traverse.listup_operators(graph), AxiswiseScale):
            flag_changed = True
            x = op.inputs["x0"]
            s = op.inputs["x1"]
            y = op.outputs["y"]
            op.remove_all()
            OptimizeRule.replace_variable(graph, (x * s).change_order(y.order), y)

            if flag_warn:
                flag_warn = False
                console.warning("AxiswiseScale will be removed in the future version. Use ElementwiseMul.", DeprecationWarning)

        return graph, flag_changed
