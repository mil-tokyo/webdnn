from enum import Enum, auto
from typing import Union

from webdnn.graph.attribute import Attribute
from webdnn.graph.variable import Variable


class ChannelModeEnum(Enum):
    RGBA = auto()
    R = auto()


class ChannelMode(Attribute):
    """
    This attribute represents the channel mode of WebGL texture buffers.

    - If this attribute is registered with a variable, it represents the data format of the variable.
    """

    def __init__(self, base: Variable, mode: ChannelModeEnum):
        if base.has_attribute(ChannelMode):
            raise ValueError(f"\'ChannelMode\' attribute has been already registered to {base}.")

        self.base = base
        self.mode = mode

    def __str__(self):
        return f"ChannelMode[{self.mode.name}]"

    @staticmethod
    def set(base: Variable, mode: ChannelModeEnum):
        if base.has_attribute(ChannelMode):
            base.get_attribute(ChannelMode)[0].mode = mode
        else:
            base.attributes.add(ChannelMode(base, mode=mode))

    @staticmethod
    def get(base: Variable):
        return base.get_attribute(ChannelMode)[0].mode if base.has_attribute(ChannelMode) else ChannelModeEnum.R

    @staticmethod
    def elements_per_pixel(mode: Union[Variable, ChannelModeEnum]):
        if isinstance(mode, Variable):
            mode = ChannelMode.get(mode)

        if mode == ChannelModeEnum.R:
            return 1

        elif mode == ChannelModeEnum.RGBA:
            return 4

        else:
            raise NotImplementedError(f"Unknown channel mode: {mode}")
