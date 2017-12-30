from typing import Optional

from webdnn.graph.attribute import Attribute
from webdnn.graph.operator import Operator


class InplaceOperator(Attribute):
    """InplaceOperator(op, input_name, output_name)

    This attribute represents that the operation can be performed as inplace for corresponding input and output variables. Note that the
    operation with this attribute is not always performed as inplace. For example, if orders of input and output variables are different,
    operation cannot be performed as inplace.

    Attributes:
        op (:class:`~webdnn.graph.operator.Operator`) : base operator
        input_name (str): input names which can be operated in-place
        output_name (str): output names which can be operated in-place
    """

    def __init__(self, op: Operator, input_name: str, output_name: str):
        self.op = op
        self.input_name = input_name
        self.output_name = output_name

    def get_input(self):
        return self.op.inputs[self.input_name]

    def get_output(self):
        return self.op.outputs[self.output_name]

    def get_status(self):
        return self.op.has_attribute(Inplace)

    def toggle_status(self, inplace: Optional[bool] = None):
        if inplace is None:
            inplace = not self.op.has_attribute(Inplace)

        if inplace:
            if self.op.has_attribute(Inplace):
                return

            self.op.attributes.add(Inplace(self.op))

        else:
            if not self.op.has_attribute(Inplace):
                return

            self.op.attributes.remove(self.op.get_attribute(Inplace)[0])


class Inplace(Attribute):
    """Inplace(op, input_name, output_name)

    Operation with this attribute is transpiled as inplace operation.

    Attributes:
        op (:class:`~webdnn.graph.operator.Operator`) : base operator
    """

    def __init__(self, op: Operator):
        self.op = op

    def get_input(self):
        return self.op.get_attribute(InplaceOperator)[0].get_input()

    def get_output(self):
        return self.op.get_attribute(InplaceOperator)[0].get_output()
