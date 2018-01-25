from typing import Tuple

from webdnn.graph.attribute import Attribute
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable


class Associative(Attribute):
    """Associative(op, var_keys)

    Associative property

    The operator with this attribute satisfies follow conditions.

        - The operator is elementwise operator.
        - The operator receives just two input variables.
        - Rearranging the parentheses in sequence of this operation will not change its value.

            .. math::

                \left( a \circ b \right) \circ c = a \circ \left( b  \circ c \right)

    Attributes:
        op (:class:`~webdnn.graph.operator.Operator`) : base operator
        var_keys (tuple of str): input names which can be swapped.
    """

    def __init__(self, op: Operator, var_keys: Tuple[str, str]):
        self.op = op
        self.var_keys = var_keys

    @property
    def vars(self):
        return tuple(self.op.inputs[key] for key in self.var_keys)

    def reorder(self, other_op: Operator):
        """
        Reorder operation

        .. code-block:: text

            (x1 + x2) + x3

            x1 -[var1]-+
                       +-{op1}- h -[var1]-+
            x2 -[var2]-+                  +-{op2}- y -
                                          |
            x3 --------------------[var2]-+

        In this case, :code:`op2_associative_attr.reorder(other_op=op1)` modified the computation graph as follows,

        .. code-block:: text

            x1 + (x2 + x3)

            x1 --------------------[var1]-+
                                          |
            x2 -[var1]-+                  +-{op1}- y -
                       +-{op2}- h -[var2]-+
            x3 -[var2]-+
        """
        if not isinstance(other_op, self.op.__class__):
            raise TypeError(f"""
The parameter "other_op" must be the instance of the same class as base operator:
    (self.op.__class__) = {self.op.__class__}
    (other_op.__class__) = {other_op.__class__}""")

        op2 = self.op
        op1 = other_op
        op1_attr = op1.get_attribute(Associative)[0]

        y = list(op2.outputs.values())[0]

        if self.vars[0].output_from == other_op:
            """
            case A: First operand is created from `other_op`: (x1 + x2) + x3

            x1 -[var1]-+
                       +-{op1}- h -[var1]-+
            x2 -[var2]-+                  +-{op2}- y -
                                          |
            x3 --------------------[var2]-+
            """
            h, x3 = self.vars
            x1, x2 = op1_attr.vars

        elif self.vars[1].output_from == other_op:
            """
            case B: Second operand is created from `other_op`: x1 + (x2 + x3)

            x1 --------------------[var1]-+
                                          |
            x2 -[var1]-+                  +-{op2}- y -
                       +-{op1}- h -[var2]-+
            x3 -[var2]-+
            """
            x1, h = self.vars
            x2, x3 = op1_attr.vars

        else:
            raise ValueError(f"""
The parameter "other_op" must be the creator of either one input variable of base operator:
    (var1.output_from) = {self.vars[0].output_from}
    (var2.output_from) = {self.vars[1].output_from}
    (other_op) = {other_op}""")

        if len(h.input_to) > 1:
            raise ValueError(f"Reordering cannot be performed. Intermediate value is used by other operator.")

        op2.replace_input(h, x2, with_assert=False)
        """
            case A: (x1+x2)+x3 => x1+(x2+x3)

            x1 -[var1]-+
                       +-{op1}- h
            x2 -[var2]-+

            x2 -[var1]-+
                       +-{op2}- y
            x3 -[var2]-+

            -------------------------------------------------------

            case B: x1+(x2+x3) => (x1+x2)+x3

            x1 -[var1]-+
                       +-{op2}- y -
            x2 -[var2]-+

            x2 -[var2]-+
                       +-{op1}- h
            x3 -[var1]-+
        """

        h_new = Variable(x2.shape, x2.order)
        op1.replace_input(x2, h_new, with_assert=False)
        """
            case A: (x1+x2)+x3 => x1+(x2+x3)

               x1 -[var1]-+
                          +-{op1}- h
            h_new -[var2]-+

            x2 -[var1]-+
                       +-{op2}- y -
            x3 -[var2]-+

            -------------------------------------------------------

            case B: x1+(x2+x3) => (x1+x2)+x3

            x1 -[var1]-+
                       +-{op2}- y -
            x2 -[var2]-+

            h_new -[var2]-+
                          +-{op1}- h
               x3 -[var1]-+
        """

        op2.replace_output(y, h_new, with_assert=False)
        """
            case A: (x1+x2)+x3 => x1+(x2+x3)

                                   x1 -[var1]-+
            x2 -[var1]-+                      +-{op1}- h
                       +-{op2}- h_new -[var2]-+
            x3 -[var2]-+

            -------------------------------------------------------

            case B: x1+(x2+x3) => (x1+x2)+x3

            x1 -[var1]-+
                       +-{op2}- h_new -[var1]-+
            x2 -[var2]-+                      +-{op1}- h
                                   x3 -[var2]-+
        """

        op1.replace_output(h, y, with_assert=False)
        """
            case A: (x1+x2)+x3 => x1+(x2+x3)

                                   x1 -[var1]-+
            x2 -[var1]-+                      +-{op1}- y -
                       +-{op2}- h_new -[var2]-+
            x3 -[var2]-+

            -------------------------------------------------------

            case B: x1+(x2+x3) => (x1+x2)+x3

            x1 -[var1]-+
                       +-{op2}- h_new -[var1]-+
            x2 -[var2]-+                      +-{op1}- y -
                                   x3 -[var2]-+
        """
