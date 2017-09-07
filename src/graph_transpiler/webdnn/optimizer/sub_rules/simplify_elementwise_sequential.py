from typing import Tuple, List

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_div import ElementwiseDiv
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
from webdnn.graph.traverse import search_sub_structure
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


def _get_constant_and_variable(op, key1, key2):
    if isinstance(op.inputs[key1], ConstantVariable):
        return op.inputs[key1], op.inputs[key2]

    elif isinstance(op.inputs[key2], ConstantVariable):
        return op.inputs[key2], op.inputs[key1]

    else:
        return None, None


class SimplifyOperatorBase(OptimizeRule):
    pattern = [Operator, Operator]  # type: List[Operator, Operator]

    def __init__(self):
        super(SimplifyOperatorBase, self).__init__()

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.SIMPLIFY_ELEMENTWISE_SEQUENTIAL
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        matches = search_sub_structure(graph, [self.pattern[0], Variable, self.pattern[1]])
        while len(matches) > 0:
            op1, v1, op2 = matches.pop()  # type: Operator, Variable, Operator

            if len(v1.input_to) > 1:
                continue

            if self.optimize_pair(op1, op2):
                flag_changed = True
                matches = search_sub_structure(graph, [self.pattern[0], Variable, self.pattern[1]])

        return graph, flag_changed

    def optimize_pair(self, op1: Operator, op2: Operator):
        raise NotImplementedError


class SimplifyScalarAddScalarAdd(SimplifyOperatorBase):
    pattern = [ScalarAdd, ScalarAdd]

    def optimize_pair(self, op1: ScalarAdd, op2: ScalarAdd):
        x0 = op1.inputs["x0"]
        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = x0 + (op1.value + op2.value)  # type: Variable
        y.replace(y2)
        return True


class SimplifyScalarAddScalarMul(SimplifyOperatorBase):
    pattern = [ScalarAdd, ScalarMul]

    def optimize_pair(self, op1: ScalarAdd, op2: ScalarMul):
        x0 = op1.inputs["x0"]
        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = (x0 * op2.value) + (op1.value * op2.value)  # type: Variable
        y.replace(y2)
        return True


class SimplifyScalarAddElementwiseAdd(SimplifyOperatorBase):
    pattern = [ScalarAdd, ElementwiseAdd]

    def optimize_pair(self, op1: ScalarAdd, op2: ElementwiseAdd):
        x0 = op1.inputs["x0"]
        y1 = op1.outputs["y"]

        if y1 == op2.inputs["x0"]:
            w = op2.inputs["x1"]
        else:
            w = op2.inputs["x0"]
        y2 = op2.outputs["y"]

        op2.remove_all()
        op1.remove_all()
        y = (x0 + w) + op1.value  # type: Variable
        y.replace(y2)
        return True


class SimplifyScalarAddElementwiseMul(SimplifyOperatorBase):
    pattern = [ScalarAdd, ElementwiseMul]

    def optimize_pair(self, op1: ScalarAdd, op2: ElementwiseMul):
        x0 = op1.inputs["x0"]
        y1 = op1.outputs["y"]

        if y1 == op2.inputs["x0"]:
            w = op2.inputs["x1"]
        else:
            w = op2.inputs["x0"]
        y2 = op2.outputs["y"]

        op2.remove_all()
        op1.remove_all()
        y = (x0 * w) + (op1.value * w)  # type: Variable
        y.replace(y2)
        return True


class SimplifyScalarAddElementwiseDiv(SimplifyOperatorBase):
    pattern = [ScalarAdd, ElementwiseDiv]

    def optimize_pair(self, op1: ScalarAdd, op2: ElementwiseDiv):
        x0 = op1.inputs["x0"]
        y1 = op1.outputs["y"]

        if y1 == op2.inputs["x0"]:
            w = op2.inputs["x1"]
        else:
            w = op2.inputs["x0"]
        y2 = op2.outputs["y"]

        op2.remove_all()
        op1.remove_all()
        y = (x0 / w) + (op1.value / w)  # type: Variable
        y.replace(y2)
        return True


class SimplifyScalarMulScalarMul(SimplifyOperatorBase):
    pattern = [ScalarMul, ScalarMul]

    def optimize_pair(self, op1: ScalarMul, op2: ScalarMul):
        x0 = op1.inputs["x0"]
        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = x0 * (op1.value * op2.value)  # type: Variable
        y.replace(y2)
        return True


class SimplifyScalarMulElementwiseMul(SimplifyOperatorBase):
    pattern = [ScalarMul, ElementwiseMul]

    def optimize_pair(self, op1: ScalarMul, op2: ElementwiseMul):
        x0 = op1.inputs["x0"]
        y1 = op1.outputs["y"]

        if y1 == op2.inputs["x0"]:
            w = op2.inputs["x1"]
        else:
            w = op2.inputs["x0"]
        y2 = op2.outputs["y"]

        op2.remove_all()
        op1.remove_all()
        y = (x0 * w) * op1.value  # type: Variable
        y.replace(y2)
        return True


class SimplifyScalarMulElementwiseDiv(SimplifyOperatorBase):
    pattern = [ScalarMul, ElementwiseDiv]

    def optimize_pair(self, op1: ScalarMul, op2: ElementwiseDiv):
        x0 = op1.inputs["x0"]
        y1 = op1.outputs["y"]

        if y1 == op2.inputs["x0"]:
            w = op2.inputs["x1"]
        else:
            w = op2.inputs["x0"]
        y2 = op2.outputs["y"]

        op2.remove_all()
        op1.remove_all()
        y = (x0 / w) * op1.value  # type: Variable
        y.replace(y2)
        return True


class SimplifyElementwiseAddScalarAdd(SimplifyOperatorBase):
    pattern = [ElementwiseAdd, ScalarAdd]

    def optimize_pair(self, op1: ElementwiseAdd, op2: ScalarAdd):
        if isinstance(op1.inputs["x0"], ConstantVariable):
            c1 = op1.inputs["x0"], v1 = op1.inputs["x1"]
        elif isinstance(op1.inputs["x1"], ConstantVariable):
            c1 = op1.inputs["x1"], v1 = op1.inputs["x0"]
        else:
            return False

        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = v1 + (c1 + op2.value)  # type: Variable
        y.replace(y2)
        return True


class SimplifyElementwiseAddScalarMul(SimplifyOperatorBase):
    pattern = [ElementwiseAdd, ScalarMul]

    def optimize_pair(self, op1: ElementwiseAdd, op2: ScalarMul):
        c1, v1 = _get_constant_and_variable(op1, "x0", "x1")
        if c1 is None:
            return False

        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = (v1 * op2.value) + (c1 * op2.value)  # type: Variable
        y.replace(y2)
        return True


class SimplifyElementwiseAddElementwiseMul(SimplifyOperatorBase):
    pattern = [ElementwiseAdd, ElementwiseMul]

    def optimize_pair(self, op1: ElementwiseAdd, op2: ElementwiseMul):
        c1, v1 = _get_constant_and_variable(op1, "x0", "x1")
        if c1 is None:
            return False

        c2, v2 = _get_constant_and_variable(op2, "x0", "x1")
        if c2 is None:
            return False

        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = (v1 * c2) + (c1 * c2)
        y.replace(y2)
        return True


class SimplifyElementwiseAddElementwiseDiv(SimplifyOperatorBase):
    pattern = [ElementwiseAdd, ElementwiseDiv]

    def optimize_pair(self, op1: ElementwiseAdd, op2: ElementwiseDiv):
        c1, v1 = _get_constant_and_variable(op1, "x0", "x1")
        if c1 is None:
            return False

        c2, v2 = _get_constant_and_variable(op2, "x0", "x1")
        if c2 is None:
            return False

        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = (v1 / c2) + (c1 / c2)
        y.replace(y2)
        return True


class SimplifyElementwiseMulScalarMul(SimplifyOperatorBase):
    pattern = [ElementwiseMul, ScalarMul]

    def optimize_pair(self, op1: ElementwiseMul, op2: ScalarMul):
        c1, v1 = _get_constant_and_variable(op1, "x0", "x1")
        if c1 is None:
            return False

        y2 = op2.outputs["y"]
        op1.remove_all()
        op2.remove_all()
        y = v1 * (c1 * op2.value)  # type: Variable
        y.replace(y2)
        return True


class SimplifyElementwiseMulElementwiseDiv(SimplifyOperatorBase):
    pattern = [ElementwiseMul, ElementwiseDiv]

    def optimize_pair(self, op1: ElementwiseMul, op2: ElementwiseDiv):
        c1, v1 = _get_constant_and_variable(op1, "x0", "x1")
        if c1 is None:
            return False

        c2, v2 = _get_constant_and_variable(op2, "x0", "x1")
        if c2 is None:
            return False

        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = v1 * (c1 / c2)
        y.replace(y2)
        return True


class SimplifyElementwiseDivScalarMul(SimplifyOperatorBase):
    pattern = [ElementwiseDiv, ScalarMul]

    def optimize_pair(self, op1: ElementwiseDiv, op2: ScalarMul):
        c1, v1 = _get_constant_and_variable(op1, "x0", "x1")
        if c1 is None:
            return False

        y2 = op2.outputs["y"]
        op1.remove_all()
        op2.remove_all()
        y = v1 * (op2.value / c1)  # type: Variable
        y.replace(y2)
        return True


class SimplifyElementwiseDivElementwiseMul(SimplifyOperatorBase):
    pattern = [ElementwiseDiv, ElementwiseMul]

    def optimize_pair(self, op1: ElementwiseDiv, op2: ElementwiseMul):
        c1, v1 = _get_constant_and_variable(op1, "x0", "x1")
        if c1 is None:
            return False

        c2, v2 = _get_constant_and_variable(op2, "x0", "x1")
        if c2 is None:
            return False

        y2 = op2.outputs["y"]
        op2.remove_all()
        op1.remove_all()
        y = v1 * (c2 / c1)
        y.replace(y2)
        return True


class SimplifyConcatElementwiseMul(SimplifyOperatorBase):
    pattern = [Concat, ElementwiseMul]

    def optimize_pair(self, op1: Concat, op2: ElementwiseMul):
        x0, x1 = op1.inputs["x0"], op1.inputs["x1"]
        c, _ = _get_constant_and_variable(op2, "x0", "x1")
        if c is None:
            return False
        if c.order != Order([op1.axis]):
            return False

        y2 = op2.outputs["y"]
        c0 = ConstantVariable(c.data[:x0.shape_dict[op1.axis]], c.order)
        c1 = ConstantVariable(c.data[x0.shape_dict[op1.axis]:], c.order)

        op1.remove_all()
        op2.remove_all()

        y, = Concat(None, axis=op1.axis)((x0 * c0), (x1 * c1))
        y.replace(y2)
        return True


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

    def __init__(self):
        super(SimplifyElementwiseSequential, self).__init__()
        self.register(SimplifyScalarAddScalarAdd())
        self.register(SimplifyScalarAddScalarMul())
        self.register(SimplifyScalarAddElementwiseAdd())
        self.register(SimplifyScalarAddElementwiseMul())
        self.register(SimplifyScalarAddElementwiseDiv())

        self.register(SimplifyScalarMulScalarMul())
        self.register(SimplifyScalarMulElementwiseMul())
        self.register(SimplifyScalarMulElementwiseDiv())

        self.register(SimplifyElementwiseAddScalarAdd())
        self.register(SimplifyElementwiseAddScalarMul())
        self.register(SimplifyElementwiseAddElementwiseMul())
        self.register(SimplifyElementwiseAddElementwiseDiv())

        self.register(SimplifyElementwiseMulScalarMul())
        self.register(SimplifyElementwiseMulElementwiseDiv())

        self.register(SimplifyElementwiseDivScalarMul())
        self.register(SimplifyElementwiseDivElementwiseMul())

        self.register(SimplifyConcatElementwiseMul())

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.SIMPLIFY_ELEMENTWISE_SEQUENTIAL
        ]
