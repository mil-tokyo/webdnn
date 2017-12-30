from typing import Tuple

import numpy as np

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.operators.scalar_pow import ScalarPow
from webdnn.graph.optimize_rule import OptimizeRule, OptimizeRuleGroup
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class ReplaceScalarAffine(OptimizeRule):
    """
    Replace :class:`ScalarAffine` into :class:`ElementwiseMul` and :class:`ElementwiseAdd`
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.REPLACE_SCALAR_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), ScalarAffine):
            x = op.inputs["x0"]
            y = op.outputs["y"]

            if not Placeholder.check_resolved(x.size) or not Placeholder.check_resolved(y.size):
                continue

            op.remove_all()

            scale = ConstantVariable(np.full(x.shape, op.scale), x.order)
            bias = ConstantVariable(np.full(x.shape, op.bias), x.order)

            y_dummy = x * scale + bias
            y_dummy.change_order(y.order)
            OptimizeRule.replace_variable(graph, y_dummy, y)

            flag_changed = True

        return graph, flag_changed


class ReplaceScalarAdd(OptimizeRule):
    """
    Replace :class:`ScalarAdd` into :class:`ElementwiseAdd`
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.REPLACE_SCALAR_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), ScalarAdd):
            x = op.inputs["x0"]
            y = op.outputs["y"]

            if not Placeholder.check_resolved(x.size) or not Placeholder.check_resolved(y.size):
                continue

            op.remove_all()

            value = ConstantVariable(np.full(x.shape, op.value), x.order)

            y_dummy = x + value
            y_dummy.change_order(y.order)
            OptimizeRule.replace_variable(graph, y_dummy, y)

            flag_changed = True

        return graph, flag_changed


class ReplaceScalarMul(OptimizeRule):
    """
    Replace :class:`ScalarMul` into :class:`ElementwiseMul`
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.REPLACE_SCALAR_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), ScalarMul):
            x = op.inputs["x0"]
            y = op.outputs["y"]

            if not Placeholder.check_resolved(x.size) or not Placeholder.check_resolved(y.size):
                continue

            op.remove_all()

            value = ConstantVariable(np.full(x.shape, op.value), x.order)

            y_dummy = x * value
            y_dummy.change_order(y.order)
            OptimizeRule.replace_variable(graph, y_dummy, y)

            flag_changed = True

        return graph, flag_changed


class ReplaceScalarPow(OptimizeRule):
    """
    Replace :class:`ScalarMul` into :class:`ElementwiseMul`
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.REPLACE_SCALAR_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for op in traverse.filter_nodes(traverse.listup_operators(graph), ScalarPow):
            x = op.inputs["x0"]
            y = op.outputs["y"]

            if not Placeholder.check_resolved(x.size) or not Placeholder.check_resolved(y.size):
                continue

            op.remove_all()

            value = ConstantVariable(np.full(x.shape, op.value), x.order)

            y_dummy = x ** value
            y_dummy.change_order(y.order)
            OptimizeRule.replace_variable(graph, y_dummy, y)

            flag_changed = True

        return graph, flag_changed


class ReplaceScalarOperator(OptimizeRuleGroup):
    def __init__(self):
        super(ReplaceScalarOperator, self).__init__([
            ReplaceScalarAffine(),
            ReplaceScalarAdd(),
            ReplaceScalarMul(),
            ReplaceScalarPow()
        ])

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.REPLACE_SCALAR_OPERATOR
        ]
