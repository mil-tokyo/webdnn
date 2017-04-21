from graph_builder.graph.attribute import Attribute
from graph_builder.graph.axis import Axis


class Axiswise(Attribute):
    axis: Axis


class Channelwise(Axiswise):
    axis = Axis.C
