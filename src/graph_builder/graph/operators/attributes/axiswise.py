from enum import Enum, auto

from graph_builder.graph.attribute import Attribute


class Axis(Enum):
    N = auto()
    C = auto()
    H = auto()
    W = auto()


class Axiswise(Attribute):
    axis: Axis


class Channelwise(Axiswise):
    axis = Axis.C
