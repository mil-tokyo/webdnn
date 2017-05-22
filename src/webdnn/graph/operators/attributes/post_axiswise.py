from webdnn.graph.attribute import Attribute
from webdnn.graph.axis import Axis
from webdnn.graph.node import Node


# FIXME: DOCS
class PostAxiswise(Attribute):
    axis: Axis

    def __init__(self, node: Node, axis: Axis):
        super(PostAxiswise, self).__init__(node)
        self.axis = axis
