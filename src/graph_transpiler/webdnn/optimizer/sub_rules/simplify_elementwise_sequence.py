from typing import Tuple, List

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_div import ElementwiseDiv
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.optimize_rule import OptimizeRule, OptimizeRuleGroup
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
            flags.optimize.SIMPLIFY_ELEMENTWISE_SEQUENCE
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False

        matches = search_sub_structure(graph, [self.pattern[0], Variable, self.pattern[1]])
        while len(matches) > 0:
            op1, v1, op2 = matches.pop()  # type: Operator, Variable, Operator

            if len(v1.input_to) > 1:
                continue

            if self.optimize_pair(graph, op1, op2):
                flag_changed = True
                matches = search_sub_structure(graph, [self.pattern[0], Variable, self.pattern[1]])

        return graph, flag_changed

    def optimize_pair(self, graph: Graph, op1: Operator, op2: Operator):
        raise NotImplementedError


class SimplifyElementwiseAddElementwiseMul(SimplifyOperatorBase):
    pattern = [ElementwiseAdd, ElementwiseMul]

    def optimize_pair(self, graph: Graph, op1: ElementwiseAdd, op2: ElementwiseMul):
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
        OptimizeRule.replace_variable(graph, y2, y.change_order(y2.order))
        return True


class SimplifyElementwiseAddElementwiseDiv(SimplifyOperatorBase):
    pattern = [ElementwiseAdd, ElementwiseDiv]

    def optimize_pair(self, graph: Graph, op1: ElementwiseAdd, op2: ElementwiseDiv):
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
        OptimizeRule.replace_variable(graph, y2, y.change_order(y2.order))
        return True


class SimplifyElementwiseMulElementwiseDiv(SimplifyOperatorBase):
    pattern = [ElementwiseMul, ElementwiseDiv]

    def optimize_pair(self, graph: Graph, op1: ElementwiseMul, op2: ElementwiseDiv):
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
        OptimizeRule.replace_variable(graph, y2, y.change_order(y2.order))
        return True


class SimplifyElementwiseDivElementwiseMul(SimplifyOperatorBase):
    pattern = [ElementwiseDiv, ElementwiseMul]

    def optimize_pair(self, graph: Graph, op1: ElementwiseDiv, op2: ElementwiseMul):
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
        OptimizeRule.replace_variable(graph, y2, y.change_order(y2.order))
        return True


class SimplifyConcatElementwiseMul(SimplifyOperatorBase):
    pattern = [Concat, ElementwiseMul]

    def optimize_pair(self, graph: Graph, op1: Concat, op2: ElementwiseMul):
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
        OptimizeRule.replace_variable(graph, y2, y.change_order(y2.order))
        return True


class SimplifyElementwiseSequence(OptimizeRuleGroup):
    """
    Simplify {elementwise,scalar}{Add,Mul}s

    1. Canonicalize operation sequence as follow format,

    .. math::

        X * S + B

    where,

    - :math:`X` : input tensor
    - :math:`S` : scale tensor
    - :math:`B` : bias tensor
    """

    def __init__(self):
        super(SimplifyElementwiseSequence, self).__init__([
            SimplifyElementwiseAddElementwiseMul(),
            SimplifyElementwiseAddElementwiseDiv(),
            SimplifyElementwiseMulElementwiseDiv(),
            SimplifyElementwiseDivElementwiseMul(),
            SimplifyConcatElementwiseMul()
        ])

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE,
            flags.optimize.SIMPLIFY_ELEMENTWISE_SEQUENCE
        ]
