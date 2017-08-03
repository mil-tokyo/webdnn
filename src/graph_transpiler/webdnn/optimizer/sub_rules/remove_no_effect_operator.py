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


def _remove_ScalarAdd(graph: Graph, op: Operator):
    if isinstance(op, ScalarAdd) and op.value == 0:
        _remove_unary_operator(graph, op)
        return True

    return False


def _remove_ScalarMul(graph: Graph, op: Operator):
    if isinstance(op, ScalarMul) and op.value == 1:
        _remove_unary_operator(graph, op)
        return True

    return False


def _remove_ScalarPow(graph: Graph, op: Operator):
    if isinstance(op, ScalarPow) and op.value == 1:
        _remove_unary_operator(graph, op)
        return True

    return False


def _remove_ScalarAffine(graph: Graph, op: Operator):
    if isinstance(op, ScalarAffine) and op.scale == 1 and op.bias == 0:
        _remove_unary_operator(graph, op)
        return True

    return False


def _remove_Reshape(graph: Graph, op: Operator):
    if isinstance(op, Reshape):
        x = op.inputs["x"]
        y = op.outputs["y"]

        if x.order == y.order and x.shape == y.shape:
            _remove_unary_operator(graph, op)
            return True

        if all(
                (axis in x.order.axes and y.shape_dict[axis] == x.shape_dict[axis]) or
                (axis not in x.order.axes and y.shape_dict[axis] == 1) for axis in y.order.axes
        ) and all(isinstance(op2, Elementwise) for op2 in y.input_to):
            op.remove_all()
            for op2 in list(y.input_to):
                name = op2._get_input_name(y)
                op2.remove_input(y)
                op2.append_input(name, x)
            return True

    return False


def _remove_Broadcast(graph: Graph, op: Operator):
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


def _remove_ElementwiseAdd(graph: Graph, op: Operator):
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


def _remove_ElementwiseMul(graph: Graph, op: Operator):
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


def _remove_ElementwiseDiv(graph: Graph, op: Operator):
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


def _remove_ElementwisePow(graph: Graph, op: Operator):
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
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.REMOVE_NO_EFFECT_OPERATOR
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        for op in traverse.listup_operators(graph):
            flag_changed |= \
                _remove_ScalarAdd(graph, op) or \
                _remove_ScalarMul(graph, op) or \
                _remove_ScalarPow(graph, op) or \
                _remove_ScalarAffine(graph, op) or \
                _remove_Reshape(graph, op) or \
                _remove_Broadcast(graph, op) or \
                _remove_ElementwiseAdd(graph, op) or \
                _remove_ElementwiseMul(graph, op) or \
                _remove_ElementwiseDiv(graph, op) or \
                _remove_ElementwisePow(graph, op)

        return graph, flag_changed
