from typing import Tuple

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.traverse import search_sub_structure
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class SimplifyElementwiseSequential(OptimizeRule):
    """
    Simplify {elementwise,scalar}{Add,Mul}s

    1. Canonicalize operation sequence as follow format,

    .. math::

        X * S * s + B + b

    where,

    - :math:`X` : input tensor
    - :math:`S` : scale tensor
    - :math:`B` : bias tensor
    - :math:`s` : scale scalar
    - :math:`b` : bias scalar

    2. Simplify operations if enable.
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.SIMPLIFY_ELEMENTWISE_SEQUENTIAL
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        matches = search_sub_structure(graph, [Elementwise, Variable, Elementwise])
        while len(matches) > 0:
            match = matches.pop()
            op1 = match[0]  # type: Operator
            op2 = match[2]  # type: Operator

            if _optimizeScalarAdd(op1, op2) or \
                _optimizeScalarMul(op1, op2) or \
                _optimizeElementwiseAdd(op1, op2) or \
                _optimizeElementwiseMul(op1, op2):
                flag_changed = True
                matches = search_sub_structure(graph, [Elementwise, Variable, Elementwise])

        return graph, flag_changed


# (ScalarAdd, _)

def _optimize_ScalarAdd_ScalarAdd(op1: ScalarAdd, op2: Operator):
    if not isinstance(op2, ScalarAdd):
        return False

    x0 = op1.inputs["x0"]
    y2 = op2.outputs["y"]
    op2.remove_all()
    op1.remove_all()
    y = x0 + (op1.value + op2.value)
    y.replace(y2)
    return True


def _optimize_ScalarAdd_ScalarMul(op1: ScalarAdd, op2: Operator):
    if not isinstance(op2, ScalarMul):
        return False

    x0 = op1.inputs["x0"]
    y2 = op2.outputs["y"]
    op2.remove_all()
    op1.remove_all()
    y = (x0 * op2.value) + (op1.value * op2.value)
    y.replace(y2)
    return True


def _optimize_ScalarAdd_ElementwiseAdd(op1: ScalarAdd, op2: Operator):
    if not isinstance(op2, ElementwiseAdd):
        return False

    x0 = op1.inputs["x0"]
    y1 = op1.outputs["y"]

    if y1 == op2.inputs["x0"]:
        w = op2.inputs["x1"]
    else:
        w = op2.inputs["x0"]
    y2 = op2.outputs["y"]

    op2.remove_all()
    op1.remove_all()
    y = (x0 + w) + op1.value
    y.replace(y2)
    return True


def _optimize_ScalarAdd_ElementwiseMul(op1: ScalarAdd, op2: Operator):
    if not isinstance(op2, ElementwiseMul):
        return False

    x0 = op1.inputs["x0"]
    y1 = op1.outputs["y"]

    if y1 == op2.inputs["x0"]:
        w = op2.inputs["x1"]
    else:
        w = op2.inputs["x0"]
    y2 = op2.outputs["y"]

    op2.remove_all()
    op1.remove_all()
    y = (x0 * w) + (op1.value * w)
    y.replace(y2)
    return True


# (ScalarMul, _)

def _optimize_ScalarMul_ScalarMul(op1: ScalarMul, op2: Operator):
    if not isinstance(op2, ScalarMul):
        return False

    x0 = op1.inputs["x0"]
    y2 = op2.outputs["y"]
    op2.remove_all()
    op1.remove_all()
    y = x0 * (op1.value * op2.value)
    y.replace(y2)
    return True


def _optimize_ScalarMul_ElementwiseMul(op1: ScalarMul, op2: Operator):
    if not isinstance(op2, ElementwiseMul):
        return False

    x0 = op1.inputs["x0"]
    y1 = op1.outputs["y"]

    if y1 == op2.inputs["x0"]:
        w = op2.inputs["x1"]
    else:
        w = op2.inputs["x0"]
    y2 = op2.outputs["y"]

    op2.remove_all()
    op1.remove_all()
    y = (x0 * w) * op1.value
    y.replace(y2)
    return True


# (ElementwiseAdd, _)

def _optimize_ElementwiseAdd_ScalarAdd(op1: ElementwiseAdd, c1: ConstantVariable, v1: Variable, op2: Operator):
    if not isinstance(op2, ScalarAdd):
        return False

    y2 = op2.outputs["y"]
    op2.remove_all()
    op1.remove_all()
    y = v1 + (c1 + op2.value)
    y.replace(y2)
    return True


def _optimize_ElementwiseAdd_ScalarMul(op1: ElementwiseAdd, c1: ConstantVariable, v1: Variable, op2: Operator):
    if not isinstance(op2, ScalarMul):
        return False

    y2 = op2.outputs["y"]
    op2.remove_all()
    op1.remove_all()
    y = (v1 * op2.value) + (c1 * op2.value)
    y.replace(y2)
    return True


def _optimize_ElementwiseAdd_ElementwiseAdd(op1: ElementwiseAdd, c1: ConstantVariable, v1: Variable, op2: Operator):
    if not isinstance(op2, ElementwiseAdd):
        return False

    x0 = op2.inputs["x0"]
    x1 = op2.inputs["x1"]
    y2 = op2.outputs["y"]
    if isinstance(x0, ConstantVariable):
        c2 = x0

    elif isinstance(x1, ConstantVariable):
        c2 = x1

    else:
        return False

    op2.remove_all()
    op1.remove_all()
    y = v1 + (c1 + c2)
    y.replace(y2)
    return True


def _optimize_ElementwiseAdd_ElementwiseMul(op1: ElementwiseAdd, c1: ConstantVariable, v1: Variable, op2: Operator):
    if not isinstance(op2, ElementwiseMul):
        return False

    x0 = op2.inputs["x0"]
    x1 = op2.inputs["x1"]
    y2 = op2.outputs["y"]
    if isinstance(x0, ConstantVariable):
        c2 = x0

    elif isinstance(x1, ConstantVariable):
        c2 = x1

    else:
        return False

    op2.remove_all()
    op1.remove_all()
    y = (v1 * c2) + (c1 * c2)
    y.replace(y2)
    return True


# (ElementwiseMul, _)

def _optimize_ElementwiseMul_ScalarMul(op1: ElementwiseMul, c1: ConstantVariable, v1: Variable, op2: Operator):
    if not isinstance(op2, ScalarMul):
        return False

    y2 = op2.outputs["y"]
    op1.remove_all()
    op2.remove_all()
    y = v1 * (c1 * op2.value)
    y.replace(y2)
    return True


def _optimize_ElementwiseMul_ElementwiseMul(op1: ElementwiseMul, c1: ConstantVariable, v1: Variable, op2: Operator):
    if not isinstance(op2, ElementwiseMul):
        return False

    x0 = op2.inputs["x0"]
    x1 = op2.inputs["x1"]
    y2 = op2.outputs["y"]
    if isinstance(x0, ConstantVariable):
        c2 = x0

    elif isinstance(x1, ConstantVariable):
        c2 = x1

    else:
        return False

    op2.remove_all()
    op1.remove_all()
    y = v1 * (c1 * c2)
    y.replace(y2)
    return True


# (_, _)

def _optimizeScalarAdd(op1: Operator, op2: Operator):
    if not isinstance(op1, ScalarAdd):
        return False

    if _optimize_ScalarAdd_ScalarAdd(op1, op2) or \
        _optimize_ScalarAdd_ScalarMul(op1, op2) or \
        _optimize_ScalarAdd_ElementwiseAdd(op1, op2) or \
        _optimize_ScalarAdd_ElementwiseMul(op1, op2):
        return True


def _optimizeScalarMul(op1: Operator, op2: Operator):
    if not isinstance(op1, ScalarMul):
        return False

    if _optimize_ScalarMul_ScalarMul(op1, op2) or \
        _optimize_ScalarMul_ElementwiseMul(op1, op2):
        return True


def _optimizeElementwiseAdd(op1: Operator, op2: Operator):
    if not isinstance(op1, ElementwiseAdd):
        return False

    x0 = op1.inputs["x0"]
    x1 = op1.inputs["x1"]
    if isinstance(x0, ConstantVariable):
        c1 = x0
        v1 = x1

    elif isinstance(x1, ConstantVariable):
        c1 = x1
        v1 = x0

    else:
        return False

    if _optimize_ElementwiseAdd_ScalarAdd(op1, c1, v1, op2) or \
        _optimize_ElementwiseAdd_ScalarMul(op1, c1, v1, op2) or \
        _optimize_ElementwiseAdd_ElementwiseAdd(op1, c1, v1, op2) or \
        _optimize_ElementwiseAdd_ElementwiseMul(op1, c1, v1, op2):
        return True


def _optimizeElementwiseMul(op1: Operator, op2: Operator):
    if not isinstance(op1, ElementwiseMul):
        return False

    x0 = op1.inputs["x0"]
    x1 = op1.inputs["x1"]
    if isinstance(x0, ConstantVariable):
        c1 = x0
        v1 = x1

    elif isinstance(x1, ConstantVariable):
        c1 = x1
        v1 = x0

    else:
        return False

    if _optimize_ElementwiseMul_ScalarMul(op1, c1, v1, op2) or \
        _optimize_ElementwiseMul_ElementwiseMul(op1, c1, v1, op2):
        return True
