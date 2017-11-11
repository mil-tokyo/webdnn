from typing import Optional

from webdnn.graph.attribute import Attribute
from webdnn.graph.node import Node
from webdnn.graph.operator import Operator


class InplaceOperator(Attribute[Operator]):
    """
    This attribute represents that the operation can be performed as inplace for corresponding input and output variables. Note that the
    operation with this attribute is not always performed as inplace. For example, if orders of input and output variables are different,
    operation cannot be performed as inplace.
    """

    def __init__(self, base: Node, input_name: str, output_name: str):
        super(InplaceOperator, self).__init__(base)
        self.input_name = input_name
        self.output_name = output_name

    def get_input(self):
        return self.base.inputs[self.input_name]

    def get_output(self):
        return self.base.outputs[self.output_name]

    def get_status(self):
        return self.base.has_attribute(Inplace)

    def toggle_status(self, inplace: Optional[bool] = None):
        if inplace is None:
            inplace = not self.base.has_attribute(Inplace)

        if inplace:
            if self.base.has_attribute(Inplace):
                return

            self.base.attributes.add(Inplace(self.base))

        else:
            if not self.base.has_attribute(Inplace):
                return

            self.base.attributes.remove(self.base.get_attribute(Inplace)[0])


class Inplace(Attribute[Operator]):
    """
    Operation with this attribute is transpiled as inplace operation.
    """

    def get_input(self):
        return self.base.get_attribute(InplaceOperator)[0].get_input()

    def get_output(self):
        return self.base.get_attribute(InplaceOperator)[0].get_output()
