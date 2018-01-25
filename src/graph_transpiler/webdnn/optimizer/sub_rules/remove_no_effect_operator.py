from typing import Tuple, Type

import numpy as np

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.broadcast import Broadcast
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_div import ElementwiseDiv
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.elementwise_pow import ElementwisePow
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.operators.scalar_pow import ScalarPow
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule, OptimizeRuleGroup
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


def _remove_unary_operator(graph: Graph, op: Operator):
    x = list(op.inputs.values())[0]
    y = list(op.outputs.values())[0]
    op.remove_all()

    OptimizeRule.replace_variable(graph, y, x, with_assert=False)


def _remove_binary_elementwise(graph: Graph, op: Operator, v: Variable):
    """
    before)

    x1 -+
        +-{op}- y -
    x2 -+

    after)

                v -

    Args:
        graph: the graph
        op: the operator which will be removed
        v: variable with which output variable is replaced
    """
    y = op.outputs["y"]
    op.remove_all()
    OptimizeRule.replace_variable(graph, v, y, with_assert=False)


class RemoveNoEffectOperatorBase(OptimizeRule):
    pattern = Operator  # type: Type[Operator]

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        for op in traverse.filter_nodes(traverse.listup_operators(graph), self.pattern):
            flag_changed |= self.optimize_operator(graph, op)

        return graph, flag_changed

    def optimize_operator(self, graph: Graph, op: Operator):
        raise NotImplementedError


class RemoveNoEffectScalarAdd(RemoveNoEffectOperatorBase):
    pattern = ScalarAdd

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_SCALAR_ADD
        ]

    def optimize_operator(self, graph: Graph, op: ScalarAdd):
        if op.value == 0:
            # x + 0  ->  x
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveNoEffectScalarMul(RemoveNoEffectOperatorBase):
    pattern = ScalarMul

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_SCALAR_MUL
        ]

    def optimize_operator(self, graph: Graph, op: ScalarMul):
        if op.value == 1:
            # x * 1  ->  x
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveNoEffectScalarPow(RemoveNoEffectOperatorBase):
    pattern = ScalarPow

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_SCALAR_POW
        ]

    def optimize_operator(self, graph: Graph, op: ScalarPow):
        if op.value == 1:
            # x^1 -> x
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveNoEffectReshape(RemoveNoEffectOperatorBase):
    pattern = Reshape

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_RESHAPE
        ]

    def optimize_operator(self, graph: Graph, op: Reshape):
        x = op.inputs["x"]
        y = op.outputs["y"]

        if x.order == y.order and x.shape == y.shape:
            # no reshape is required
            _remove_unary_operator(graph, op)
            return True

        if x.shape == y.shape:
            # only reinterpret_axis is required
            op.remove_all()
            y_dummy = x.reinterpret_axes(y.order)
            OptimizeRule.replace_variable(graph, y_dummy, y)
            return True

        return False


class RemoveNoEffectTranspose(RemoveNoEffectOperatorBase):
    pattern = Transpose

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_TRANSPOSE
        ]

    def optimize_operator(self, graph: Graph, op: Transpose):
        x = op.inputs["x0"]
        y = op.outputs["y"]

        if x.order == y.order:
            # No transpose is required
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveNoEffectBroadcast(RemoveNoEffectOperatorBase):
    pattern = Broadcast

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_BROADCAST
        ]

    def optimize_operator(self, graph: Graph, op: Broadcast):
        y = op.outputs["y"]
        if y not in graph.outputs and all(isinstance(op2, Elementwise) for op2 in y.input_to):
            # If y is input to only elementwise operators, broadcast is not required.
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveNoEffectReinterpretAxis(RemoveNoEffectOperatorBase):
    pattern = ReinterpretAxis

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_REINTERPRET_AXIS
        ]

    def optimize_operator(self, graph: Graph, op: ReinterpretAxis):
        x = op.inputs["x"]
        y = op.outputs["y"]

        if op.parameters["in_order"] == op.parameters["out_order"]:
            _remove_unary_operator(graph, op)
            return True

        if x in graph.inputs and len(x.input_to) == 1:
            # before)
            #
            # x[Graph Input] -{ReinterpretAxis}- h -{op}->
            #
            # after)
            #
            # h[Graph Input] -{op}->

            op.remove_all()
            OptimizeRule.replace_variable(graph, x, y, with_assert=False)
            return True

        return False


class RemoveNoEffectElementwiseAdd(RemoveNoEffectOperatorBase):
    pattern = ElementwiseAdd

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_ELEMENTWISE_ADD
        ]

    def optimize_operator(self, graph: Graph, op: ElementwiseAdd):
        if isinstance(op.inputs["x0"], ConstantVariable):
            c = op.inputs["x0"]  # type: ConstantVariable
            v = op.inputs["x1"]  # type: Variable

        elif isinstance(op.inputs["x1"], ConstantVariable):
            v = op.inputs["x0"]  # type: Variable
            c = op.inputs["x1"]  # type: ConstantVariable

        else:
            return False

        if np.all(c.data == 0):
            # x + 0 -> x
            _remove_binary_elementwise(graph, op, v)
            return True

        return False


class RemoveNoEffectElementwiseMul(RemoveNoEffectOperatorBase):
    pattern = ElementwiseMul

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_ELEMENTWISE_MUL
        ]

    def optimize_operator(self, graph: Graph, op: ElementwiseMul):
        if isinstance(op.inputs["x0"], ConstantVariable):
            c = op.inputs["x0"]  # type: ConstantVariable
            v = op.inputs["x1"]  # type: Variable

        elif isinstance(op.inputs["x1"], ConstantVariable):
            v = op.inputs["x0"]  # type: Variable
            c = op.inputs["x1"]  # type: ConstantVariable

        else:
            return False

        if np.all(c.data == 1):
            # x * 1 -> x
            _remove_binary_elementwise(graph, op, v)
            return True

        return False


class RemoveNoEffectElementwiseDiv(RemoveNoEffectOperatorBase):
    pattern = ElementwiseDiv

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_ELEMENTWISE_DIV
        ]

    def optimize_operator(self, graph: Graph, op: ElementwiseDiv):
        if isinstance(op.inputs["x0"], ConstantVariable):
            c = op.inputs["x0"]  # type: ConstantVariable
            v = op.inputs["x1"]  # type: Variable

        elif isinstance(op.inputs["x1"], ConstantVariable):
            v = op.inputs["x0"]  # type: Variable
            c = op.inputs["x1"]  # type: ConstantVariable

        else:
            return False

        if np.all(c.data == 1):
            # x / 1 -> x
            _remove_binary_elementwise(graph, op, v)
            return True

        return False


class RemoveNoEffectElementwisePow(RemoveNoEffectOperatorBase):
    pattern = ElementwisePow

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR,
            flags.optimize.REMOVE_NO_EFFECT_ELEMENTWISE_POW
        ]

    def optimize_operator(self, graph: Graph, op: ElementwisePow):
        if isinstance(op.inputs["x0"], ConstantVariable):
            c = op.inputs["x0"]  # type: ConstantVariable
            v = op.inputs["x1"]  # type: Variable

        elif isinstance(op.inputs["x1"], ConstantVariable):
            v = op.inputs["x0"]  # type: Variable
            c = op.inputs["x1"]  # type: ConstantVariable

        else:
            return False

        if np.all(c.data == 1):
            # x^1 -> x
            _remove_binary_elementwise(graph, op, v)
            return True

        return False


class RemoveNoEffectOperator(OptimizeRuleGroup):
    def __init__(self):
        super(RemoveNoEffectOperator, self).__init__([
            RemoveNoEffectScalarAdd(),
            RemoveNoEffectScalarMul(),
            RemoveNoEffectScalarPow(),
            RemoveNoEffectReshape(),
            RemoveNoEffectTranspose(),
            RemoveNoEffectBroadcast(),
            RemoveNoEffectElementwiseAdd(),
            RemoveNoEffectElementwiseMul(),
            RemoveNoEffectElementwiseDiv(),
            RemoveNoEffectElementwisePow(),
            RemoveNoEffectReinterpretAxis()
        ])

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR
        ]
