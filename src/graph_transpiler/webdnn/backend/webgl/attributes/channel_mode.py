from enum import Enum, auto

from webdnn.graph.attribute import Attribute
from webdnn.graph.node import Node
from webdnn.graph.operator import Operator


class ChannelModeEnum(Enum):
    RGBA = auto()
    R = auto()


class ChannelMode(Attribute):
    """
    This attribute represents the channel mode of WebGL texture buffers.

    - If this attribute is registered with a variable, it represents the data format of the variable.
    - If this attribute is registered with an operator,  it represents the data format which this operator expects as input and output
        variables
    """

    def __init__(self, base: Node, mode: ChannelModeEnum):
        if base.has_attribute(ChannelMode):
            raise ValueError(f"\'ChannelMode\' attribute has been already registered to {base}.")

        super(ChannelMode, self).__init__(base)
        self.mode = mode  # type: ChannelModeEnum

    def __str__(self):
        return f"ChannelMode[{self.mode.name}]"


class SupportedChannelMode(Attribute):
    """
    This attribute represents the supported channel mode of operators
    """

    def __init__(self, op: Operator, mode: ChannelModeEnum):
        super(SupportedChannelMode, self).__init__(op)
        self.mode = mode  # type: ChannelModeEnum

    def __str__(self):
        return f"SupportedChannelMode[{self.mode.name}]"
