from typing import Tuple, Type

import numpy as np

from webdnn.frontend.constraints import AxisVar
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
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.operators.scalar_pow import ScalarPow
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


def _remove_unary_operator(graph: Graph, op: Operator):
    x = list(op.inputs.values())[0]
    y = list(op.outputs.values())[0]
    op.remove_all()

    OptimizeRule.replace_variable(graph, y, x)


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
    y.change_order(v.order)
    v.replace(y)

    if v in graph.inputs:
        if y in graph.outputs:
            index = graph.outputs.index(y)
            graph.outputs.remove(y)
            graph.outputs.insert(index, v)

        else:
            y.replace(v)

    else:
        v.replace(y)


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

        for op in traverse.filter_nodes(traverse.listup_operators(graph), self.pattern):  # type: Operator
            flag_changed |= self.optimize_operator(graph, op)

        return graph, flag_changed

    def optimize_operator(self, graph: Graph, op: Operator):
        raise NotImplementedError


class RemoveScalarAdd(RemoveNoEffectOperatorBase):
    pattern = ScalarAdd

    def optimize_operator(self, graph: Graph, op: ScalarAdd):
        if op.value == 0:
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveScalarMul(RemoveNoEffectOperatorBase):
    pattern = ScalarMul

    def optimize_operator(self, graph: Graph, op: ScalarMul):
        if op.value == 1:
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveScalarPow(RemoveNoEffectOperatorBase):
    pattern = ScalarPow

    def optimize_operator(self, graph: Graph, op: ScalarPow):
        if op.value == 1:
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveScalarAffine(RemoveNoEffectOperatorBase):
    pattern = ScalarAffine

    def optimize_operator(self, graph: Graph, op: ScalarAffine):
        if op.scale == 1 and op.bias == 0:
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveReshape(RemoveNoEffectOperatorBase):
    pattern = Reshape

    def optimize_operator(self, graph: Graph, op: Reshape):
        x = op.inputs["x"]
        y = op.outputs["y"]

        if x.order == y.order and x.shape == y.shape:
            # no reshape is occurred
            _remove_unary_operator(graph, op)
            return True

        if x.shape == y.shape:
            # only reinterpret_axis is occurred
            op.remove_all()
            y_dummy, = ReinterpretAxis(None, in_order=x.order, out_order=y.order)(x)
            y_dummy.replace(y)
            return True

        return False


class RemoveTranspose(RemoveNoEffectOperatorBase):
    pattern = Transpose

    def optimize_operator(self, graph: Graph, op: Transpose):
        x = op.inputs["x0"]
        y = op.outputs["y"]

        if x.order == y.order:
            _remove_unary_operator(graph, op)
            return True

        if x not in graph.inputs and isinstance(x.output_from, Elementwise):
            # If x is output from elementwise operator, transpose is not needed.
            x.change_order(y.order)
            _remove_unary_operator(graph, op)
            return True

        if y not in graph.outputs and all(isinstance(op2, Elementwise) for op2 in y.input_to):
            # If y is input to only elementwise operators, transpose is not needed.
            y.change_order(x.order)
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveBroadcast(RemoveNoEffectOperatorBase):
    pattern = Broadcast

    def optimize_operator(self, graph: Graph, op: Broadcast):
        y = op.outputs["y"]
        if y not in graph.outputs and all(isinstance(op2, Elementwise) for op2 in y.input_to):
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveReinterpretAxis(RemoveNoEffectOperatorBase):
    pattern = ReinterpretAxis

    def optimize_operator(self, graph: Graph, op: ReinterpretAxis):
        x = op.inputs["x"]
        y = op.outputs["y"]

        if len(x.input_to) == 1 and x.output_from is None:
            op.remove_all()

            if isinstance(x, ConstantVariable):
                x = ConstantVariable(x.data, y.order)

                if y in graph.outputs:
                    index = graph.outputs.index(y)
                    graph.outputs.remove(y)
                    graph.outputs.insert(index, x)

                else:
                    y.replace(x)
            else:
                assert x in graph.inputs

                index = graph.inputs.index(x)
                graph.inputs.remove(x)
                graph.inputs.insert(index, y)

            return True

        if op.parameters["in_order"] == op.parameters["out_order"]:
            _remove_unary_operator(graph, op)
            return True

        flag_changed = False
        for axis1, axis2 in zip(op.parameters["in_order"].axes, op.parameters["out_order"].axes):
            is_resolved1 = not (isinstance(axis1, AxisVar) and axis1.value is None)
            is_resolved2 = not (isinstance(axis2, AxisVar) and axis2.value is None)

            if is_resolved1 and not is_resolved2:
                axis2.unify(axis1)
                flag_changed = True

            elif not is_resolved1 and is_resolved2:
                axis1.unify(axis2)
                flag_changed = True

        if flag_changed:
            return True

        return False


class RemoveElementwiseAdd(RemoveNoEffectOperatorBase):
    pattern = ElementwiseAdd

    def optimize_operator(self, graph: Graph, op: ElementwiseAdd):
        if isinstance(op.inputs["x0"], ConstantVariable):
            c = op.inputs["x0"]
            v = op.inputs["x1"]

        elif isinstance(op.inputs["x1"], ConstantVariable):
            v = op.inputs["x0"]
            c = op.inputs["x1"]

        else:
            return False

        if np.all(c == 0):
            _remove_binary_elementwise(graph, op, v)
            return True

        return False


class RemoveElementwiseMul(RemoveNoEffectOperatorBase):
    pattern = ElementwiseMul

    def optimize_operator(self, graph: Graph, op: ElementwiseMul):
        if isinstance(op.inputs["x0"], ConstantVariable):
            c = op.inputs["x0"]
            v = op.inputs["x1"]

        elif isinstance(op.inputs["x1"], ConstantVariable):
            v = op.inputs["x0"]
            c = op.inputs["x1"]

        else:
            return False

        if np.all(c == 1):
            _remove_binary_elementwise(graph, op, v)
            return True

        return False


class RemoveElementwiseDiv(RemoveNoEffectOperatorBase):
    pattern = ElementwiseDiv

    def optimize_operator(self, graph: Graph, op: ElementwiseDiv):
        if isinstance(op.inputs["x0"], ConstantVariable):
            c = op.inputs["x0"]
            v = op.inputs["x1"]

        elif isinstance(op.inputs["x1"], ConstantVariable):
            v = op.inputs["x0"]
            c = op.inputs["x1"]

        else:
            return False

        if np.all(c == 1):
            _remove_binary_elementwise(graph, op, v)
            return True

        return False


class RemoveElementwisePow(RemoveNoEffectOperatorBase):
    pattern = ElementwisePow

    def optimize_operator(self, graph: Graph, op: ElementwisePow):
        if isinstance(op.inputs["x0"], ConstantVariable):
            c = op.inputs["x0"]
            v = op.inputs["x1"]

        elif isinstance(op.inputs["x1"], ConstantVariable):
            v = op.inputs["x0"]
            c = op.inputs["x1"]

        else:
            return False

        if np.all(c == 1):
            _remove_binary_elementwise(graph, op, v)
            return True

        return False


class RemoveNoEffectOperator(OptimizeRule):
    def __init__(self):
        super(RemoveNoEffectOperator, self).__init__()
        self.register(RemoveScalarAdd())
        self.register(RemoveScalarMul())
        self.register(RemoveScalarPow())
        self.register(RemoveScalarAffine())
        self.register(RemoveReshape())
        self.register(RemoveTranspose())
        self.register(RemoveBroadcast())
        self.register(RemoveElementwiseAdd())
        self.register(RemoveElementwiseMul())
        self.register(RemoveElementwiseDiv())
        self.register(RemoveElementwisePow())
        self.register(RemoveReinterpretAxis())

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR
        ]
