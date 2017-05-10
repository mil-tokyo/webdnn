from graph_transpiler.graph.attribute import Attribute
from graph_transpiler.graph.axis import Axis


# FIXME: DOCS
class Axiswise(Attribute):
    axis: Axis


class Channelwise(Axiswise):
    axis = Axis.C
