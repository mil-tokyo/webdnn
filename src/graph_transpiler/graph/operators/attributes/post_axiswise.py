from graph_transpiler.graph.attribute import Attribute
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.node import Node


# FIXME: DOCS
class PostAxiswise(Attribute):
    axis: Axis

    def __init__(self, node: Node, axis: Axis):
        super(PostAxiswise, self).__init__(node)
        self.axis = axis
