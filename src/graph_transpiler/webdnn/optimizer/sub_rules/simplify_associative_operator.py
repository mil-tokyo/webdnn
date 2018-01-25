from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.attributes.associative import Associative
from webdnn.graph.operators.attributes.commutative import Commutative
from webdnn.graph.optimize_rule import OptimizeRule, OptimizeRuleGroup
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.util import flags


class SimplifyAssociativeOperatorLeftHand(OptimizeRule):
    """
    Simplify expression which consists of same associative operator, and left hand operand has subtree, like `(v1 + v2) + v3`.

    a. If `v3` and one of `v1` or `v2` are constant variables, fold them at compile time, as `(v1 + v3) + v2`.
    b. If either `v1` or `v2` is constant variable, sweep out it as `(v1 + v3) + v2`. This optimization improves potential of
        constant folding.
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ASSOCIATIVE_OPERATOR,
            flags.optimize.SIMPLIFY_ASSOCIATIVE_OPERATOR_LEFT_HAND
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op1 in traverse.filter_nodes(traverse.listup_operators(graph), Associative):
            associative1 = op1.get_attribute(Associative)[0]
            var1, var2 = associative1.vars
            op2 = var1.output_from

            """
            {op2}- var1 -+
                         +-{op1}-
                   var2 -+
            """

            if op2 is None:
                # Left hand operand(var1) has no parent tree
                continue

            if var1 in graph.outputs or len(var1.input_to) > 1:
                # This optimization rule will remove var1
                continue

            if not isinstance(op2, op1.__class__):
                # op1 and op2 must be same operator class
                continue

            associative2 = op2.get_attribute(Associative)[0]
            var3, var4 = associative2.vars

            """
            (var3 * var4) * var2

            var3 -+
                  +-{op2}- var1 -+
            var4 -+              +-{op1}-
                           var2 -+
            """

            if isinstance(var3, ConstantVariable) and isinstance(var4, ConstantVariable):
                # No optimization is needed
                continue

            elif isinstance(var3, ConstantVariable):
                if isinstance(var2, ConstantVariable):
                    """
                    case a) Fold VAR3 and VAR2

                    initial state:

                        (VAR3 * var4) * VAR2

                    commutative2.swap()

                        (var4 * VAR3) * VAR2

                    associative1.reorder:

                        var4 * (VAR3 * VAR2)

                    """
                    if not op2.has_attribute(Commutative):
                        continue

                    commutative2 = op2.get_attribute(Commutative)[0]
                    commutative2.swap()
                    associative1.reorder(op2)
                    flag_changed = True

                else:
                    """
                    case b) Sweep out VAR3

                    initial state:

                        (VAR3 * var4) * var2

                    associative1.reorder:

                        VAR3 * (var4 * var2)
                    """
                    associative1.reorder(op2)
                    flag_changed = True

            elif isinstance(var4, ConstantVariable):
                if isinstance(var2, ConstantVariable):
                    """
                    case a) Fold VAR4 and VAR2

                    initial state:

                        (var3 * VAR4) * VAR2

                    associative1.reorder:

                        var3 * (VAR4 * VAR2)

                    """
                    associative1.reorder(op2)
                    flag_changed = True

                else:
                    """
                    case b) Sweep out var4

                    initial state:

                        (var3 * VAR4) * var2

                    commutative2.swap:

                        (VAR4 * var3) * var2

                    associative1.reorder:

                        VAR4 * (var3 * var2)
                    """
                    if not op2.has_attribute(Commutative):
                        continue

                    commutative2 = op2.get_attribute(Commutative)[0]
                    commutative2.swap()
                    associative1.reorder(op2)
                    flag_changed = True

        return graph, flag_changed


class SimplifyAssociativeOperatorRightHand(OptimizeRule):
    """
    Simplify expression which consists of same associative operator, and right hand operand has subtree, like `v1 + (v2 + v3)`.

    a. If `v1` and `v3` are constant variables, fold them at compile time, as `v2 + (v1 + v3)`.
    b. If either `v1` or `v3` is constant variable, sweep out it as `(v2 + v1) + v3`. This optimization improves potential of
        constant folding.
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ASSOCIATIVE_OPERATOR,
            flags.optimize.SIMPLIFY_ASSOCIATIVE_OPERATOR_RIGHT_HAND
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op1 in traverse.filter_nodes(traverse.listup_operators(graph), Associative):
            associative1 = op1.get_attribute(Associative)[0]
            var1, var2 = associative1.vars
            op2 = var2.output_from

            """
                   var1 -+
                         +-{op1}-
            {op2}- var2 -+
            """

            if op2 is None:
                # Right hand operand(var2) has no child tree
                continue

            if var2 in graph.outputs or len(var2.input_to) > 1:
                # This optimization rule will remove var2
                continue

            if not isinstance(op2, op1.__class__):
                # op1 and op2 must be same operator class
                continue

            associative2 = op2.get_attribute(Associative)[0]
            var3, var4 = associative2.vars

            """
            var1 * (var3 * var4)

                           var1 -+
            var3 -+              +-{op1}-
                  +-{op2}- var2 -+
            var4 -+
            """
            if isinstance(var3, ConstantVariable) and isinstance(var4, ConstantVariable):
                # No optimization is needed
                continue

            elif isinstance(var3, ConstantVariable):
                if isinstance(var1, ConstantVariable):
                    """
                    case a) Fold VAR1 and VAR3

                    initial state:

                        VAR1 * (VAR3 * var4)

                    associative1.reorder:

                        (VAR1 * VAR3) * var4

                    """
                    associative1.reorder(op2)
                    flag_changed = True

                else:
                    """
                    case b) Sweep out VAR3

                    initial state:

                        var1 * (VAR3 * var4)

                    commutative2.swap()

                        var1 * (var4 * VAR3)

                    associative1.reorder:

                        (var1 * var4) * VAR3

                    """
                    if not op2.has_attribute(Commutative):
                        continue

                    commutative2 = op2.get_attribute(Commutative)[0]
                    commutative2.swap()
                    associative1.reorder(op2)

            elif isinstance(var4, ConstantVariable):
                if isinstance(var1, ConstantVariable):
                    """
                    case a) Fold VAR4 and VAR1

                    initial state:

                        VAR1 * (var3 * VAR4)

                    commutative2.reorder:

                        VAR1 * (VAR4 * var3)

                    associative1.reorder:

                        (VAR1 * VAR4) * var3

                    """
                    if not op2.has_attribute(Commutative):
                        continue

                    commutative2 = op2.get_attribute(Commutative)[0]
                    commutative2.swap()
                    associative1.reorder(op2)
                    flag_changed = True

                else:
                    """
                    case b) Sweep out VAR4

                    initial state:

                        var1 * (var3 * VAR4)

                    associative1.reorder:

                        (var1 * var3) * VAR4
                    """
                    associative1.reorder(op2)
                    flag_changed = True

        return graph, flag_changed


class SimplifyAssociativeOperator(OptimizeRuleGroup):
    """
    Simplify expression which consists of same associative operator like `v1 + v2 + v3`.
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ASSOCIATIVE_OPERATOR
        ]

    def __init__(self):
        super(SimplifyAssociativeOperator, self).__init__([
            SimplifyAssociativeOperatorRightHand(),
            ConstantFolding(),
            SimplifyAssociativeOperatorLeftHand(),
            ConstantFolding()
        ])
