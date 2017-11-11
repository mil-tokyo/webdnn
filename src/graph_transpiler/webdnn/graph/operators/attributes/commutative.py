from typing import Tuple

from webdnn.graph.attribute import Attribute
from webdnn.graph.operator import Operator


class Commutative(Attribute[Operator]):
    """Commutative(op, var_keys)
    Commutative property

    The operator with this attribute satisfies follow conditions.

        - The operator is elementwise operator.
        - The operator receives just two input variables.
        - When the order of these input variables is changed, the result is not changed.

    Attributes:
        var_keys (tuple of str): input names which can be swapped.
    """

    def __init__(self, op: Operator, var_keys: Tuple[str, str]):
        super(Commutative, self).__init__(op)
        self.var_keys = var_keys

    @property
    def vars(self):
        return tuple(self.base.inputs[key] for key in self.var_keys)

    def swap(self):
        """
        Swap the order of input variables
        """
        var1_key, var2_key = self.var_keys
        var1, var2 = self.vars
        op = self.base

        op.remove_input(var1)
        op.remove_input(var2)
        op.append_input(var2_key, var1)
        op.append_input(var1_key, var2)
