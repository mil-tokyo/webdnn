from webdnn.graph import operator
from webdnn.graph.attribute import Attribute
from webdnn.graph.node import Node


# FIXME: DOCS
class Inplace(Attribute):
    input_name: str
    output_name: str

    def __init__(self, base: Node, input_name: str, output_name: str):
        super(Inplace, self).__init__(base)
        self.input_name = input_name
        self.output_name = output_name

    def get_input(self):
        op = self.base  # type: operator.Operator
        return op.inputs[self.input_name]

    def get_output(self):
        op = self.base  # type: operator.Operator
        return op.outputs[self.output_name]
