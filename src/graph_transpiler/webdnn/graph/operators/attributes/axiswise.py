from webdnn.graph.attribute import Attribute
from webdnn.graph.axis import Axis
from webdnn.graph.node import Node


# FIXME: DOCS
class Axiswise(Attribute):
    axis: Axis

    def __init__(self, base: Node, axis: Axis):
        super(Axiswise, self).__init__(base)
        self.axis = axis
