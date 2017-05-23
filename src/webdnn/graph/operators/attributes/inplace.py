from webdnn.graph.attribute import Attribute
from webdnn.graph.interface import IOperator
from webdnn.graph.node import Node


# FIXME: DOCS
class Inplace(Attribute):
    input_name: str
    output_name: str

    def __init__(self, node: Node, input_name: str, output_name: str):
        super(Inplace, self).__init__(node)
        self.input_name = input_name
        self.output_name = output_name

    def get_input(self):
        op = self.node  # type: IOperator
        return op.inputs[self.input_name]

    def get_output(self):
        op = self.node  # type: IOperator
        return op.outputs[self.output_name]
