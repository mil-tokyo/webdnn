from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.attributes.inplace import InplaceOperator
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class UpdateInplaceAttribute(OptimizeRule):
    """
    Update operations' inplace attributes
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.OPTIMIZE_INPLACE_OPERATION
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        for op in traverse.filter_nodes(traverse.listup_operators(graph), InplaceOperator):
            attr = op.get_attribute(InplaceOperator)[0]
            v_in = attr.get_input()
            v_out = attr.get_output()

            flag_inplace = True

            if v_in.has_attribute(Input):
                # Input variable cannot be overwritten.
                flag_inplace = False

            if isinstance(v_in, ConstantVariable):
                # Constant variable cannot be overwritten
                flag_inplace = False

            if any(v_in.stride_dict[a] != v_out.stride_dict[a] for a in v_out.order.axes if a in v_in.order.axes):
                flag_inplace = False

            if flag_inplace != attr.get_status():
                attr.toggle_status(flag_inplace)
                flag_changed = True

        return graph, flag_changed
