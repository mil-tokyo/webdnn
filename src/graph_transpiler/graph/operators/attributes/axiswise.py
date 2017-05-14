from graph_transpiler.graph.attribute import Attribute
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.node import Node


# FIXME: DOCS
class Axiswise(Attribute):
    axis: Axis

    def __init__(self, node: Node, axis: Axis):
        super(Axiswise, self).__init__(node)
        self.axis = axis
