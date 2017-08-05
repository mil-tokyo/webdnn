from typing import Tuple

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
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.operators.scalar_pow import ScalarPow
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


def _remove_unary_operator(graph: Graph, op: Operator):
    x = list(op.inputs.values())[0]
    y = list(op.outputs.values())[0]
    op.remove_all()
    y.change_order(x.order)
    if x in graph.inputs:
        if y in graph.outputs:
            index = graph.outputs.index(y)
            graph.outputs.remove(y)
            graph.outputs.insert(index, x)

        else:
            y.replace(x)

    else:
        x.replace(y)


def _remove_binary_elementwise(graph: Graph, op: Operator, v: Variable):
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
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        for op in traverse.listup_operators(graph):
            flag_changed |= self.optimize_operator(graph, op)

        return graph, flag_changed

    def optimize_operator(self, graph: Graph, op: Operator):
        raise NotImplementedError


class RemoveScalarAdd(RemoveNoEffectOperatorBase):
    def optimize_operator(self, graph: Graph, op: ScalarAdd):
        if isinstance(op, ScalarAdd) and op.value == 0:
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveScalarMul(RemoveNoEffectOperatorBase):
    def optimize_operator(self, graph: Graph, op: ScalarMul):
        if isinstance(op, ScalarMul) and op.value == 1:
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveScalarPow(RemoveNoEffectOperatorBase):
    def optimize_operator(self, graph: Graph, op: ScalarPow):
        if isinstance(op, ScalarPow) and op.value == 1:
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveScalarAffine(RemoveNoEffectOperatorBase):
    def optimize_operator(self, graph: Graph, op: ScalarAffine):
        if isinstance(op, ScalarAffine) and op.scale == 1 and op.bias == 0:
            _remove_unary_operator(graph, op)
            return True

        return False


class RemoveReshape(RemoveNoEffectOperatorBase):
    def optimize_operator(self, graph: Graph, op: Reshape):
        if isinstance(op, Reshape):
            x = op.inputs["x"]
            y = op.outputs["y"]

            if x.order == y.order and x.shape == y.shape:
                _remove_unary_operator(graph, op)
                return True

            if all([
                all(x.stride_dict[axis] == y.stride_dict[axis] for axis in set(x.order.axes) and set(y.order.axes)),
                all(isinstance(op2, Elementwise) for op2 in y.input_to),
                    y not in graph.outputs
            ]):
                op.remove_all()
                for op2 in list(y.input_to):
                    name = op2._get_input_name(y)
                    op2.remove_input(y)
                    op2.append_input(name, x)
                return True

        return False


class RemoveBroadcast(RemoveNoEffectOperatorBase):
    def optimize_operator(self, graph: Graph, op: Broadcast):
        if isinstance(op, Broadcast):
            x = op.inputs["x0"]
            y = op.outputs["y"]

            if all(isinstance(op2, Elementwise) for op2 in y.input_to):
                op.remove_all()
                for op2 in list(y.input_to):
                    name = op2._get_input_name(y)
                    op2.remove_input(y)
                    op2.append_input(name, x)
                return True

        return False


class RemoveElementwiseAdd(RemoveNoEffectOperatorBase):
    def optimize_operator(self, graph: Graph, op: ElementwiseAdd):
        if not isinstance(op, ElementwiseAdd):
            return False

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
    def optimize_operator(self, graph: Graph, op: ElementwiseMul):
        if not isinstance(op, ElementwiseMul):
            return False

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
    def optimize_operator(self, graph: Graph, op: ElementwiseDiv):
        if not isinstance(op, ElementwiseDiv):
            return False

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
    def optimize_operator(self, graph: Graph, op: ElementwisePow):
        if not isinstance(op, ElementwisePow):
            return False

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
        self.register(RemoveBroadcast())
        self.register(RemoveElementwiseAdd())
        self.register(RemoveElementwiseMul())
        self.register(RemoveElementwiseDiv())
        self.register(RemoveElementwisePow())

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR
        ]
