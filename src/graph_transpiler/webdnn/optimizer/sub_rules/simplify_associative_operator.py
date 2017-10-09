from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.associative import Associative
from webdnn.graph.operators.attributes.commutative import Commutative
from webdnn.graph.optimize_rule import OptimizeRule, OptimizeRuleGroup
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.util import flags


class SimplifyAssociativeOperatorLeftHand(OptimizeRule):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ASSOCIATIVE_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op1 in traverse.filter_nodes(traverse.listup_operators(graph), Associative):  # type: Operator
            associative1 = op1.get_attribute(Associative)[0]
            var1, var2 = associative1.vars
            op2 = var1.output_from

            if isinstance(var1, ConstantVariable):
                # Left hand operand(var1) has no child tree
                continue

            if var1 in graph.outputs or len(var1.input_to) > 1:
                # var1 will be removed in this optimize rule
                continue

            if not isinstance(op2, op1.__class__):
                # op1 and op2 must be same operator class
                continue

            associative2 = op2.get_attribute(Associative)[0]
            var3, var4 = associative2.vars

            if not isinstance(var4, ConstantVariable):
                # No optimization is needed.
                # If either var3 or var4 is constant, then it is var4 because optimization rule of commutative operator reorder operands to
                # gather constant variables for right hand.
                continue

            """
            var3 -+
                  +-{op2}- var1 -+
            var4 -+              +-{op1}-
                           var2 -+
            """

            if isinstance(var2, ConstantVariable):
                # Fold var4 and var2
                associative1.reorder(op2)  # (var3*var4)*var2 => var3*(var4*var2)
                flag_changed = True

            else:
                # Sweep out var4
                if not op1.has_attribute(Commutative):
                    continue

                associative2 = op2.get_attribute(Associative)[0]
                commutative2 = op2.get_attribute(Commutative)[0]

                if not isinstance(associative2.vars[1], ConstantVariable):
                    continue

                commutative2.swap()  # (var3*var4)*var2 => (var4*var3)*var2
                associative1.reorder(op2)  # (var4*var3)*var2 => var4*(var3*var2)
                flag_changed = True

        return graph, flag_changed


class SimplifyAssociativeOperatorRightHand(OptimizeRule):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ASSOCIATIVE_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), Associative):  # type: Operator
            associative1 = op.get_attribute(Associative)[0]
            var1, var2 = associative1.vars
            op2 = var2.output_from

            if isinstance(var2, ConstantVariable):
                # Right hand operand(var2) has no child tree
                continue

            if var2 in graph.outputs or len(var2.input_to) > 1:
                # var2 will be removed in this optimize rule
                continue

            if not isinstance(op2, op.__class__):
                # op1 and op2 must be same operator class
                continue

            associative2 = op2.get_attribute(Associative)[0]
            var3, var4 = associative2.vars
            if not isinstance(var4, ConstantVariable):
                # No optimization is needed.
                # If either var3 or var4 is constant, then it is var4 because optimization rule of commutative operator reorder operands to
                # gather constant variables for right hand.
                continue

            """
                             var1 -+
              var3 -+              +-{op1}-
                    +-{op2}- var2 -+
            const4 -+
            """

            # Sweep out var4
            associative1.reorder(op2)  # var1 *(var3*const4) => (var1*var3)*const4
            flag_changed = True

        return graph, flag_changed


class SimplifyAssociativeOperator(OptimizeRuleGroup):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE
        ]

    def __init__(self):
        super(SimplifyAssociativeOperator, self).__init__([
            SimplifyAssociativeOperatorRightHand(),
            ConstantFolding(),
            SimplifyAssociativeOperatorLeftHand(),
            ConstantFolding()
        ])
