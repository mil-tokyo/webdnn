from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.variable import Variable


class ConvertRtoRGBA(Elementwise):
    """ConvertRtoRGBA(name)
    Convert WebGL texture buffer channel mode from R to RGBA

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable whose channel mode is R.
        - **y** - Output variable whose channel mode is RGBA.
    """

    def __call__(self, x0: Variable):
        ys = super(ConvertRtoRGBA, self).__call__(x0)
        for y in ys:
            y.attributes.add(ChannelMode(y, ChannelModeEnum.RGBA))
        return ys
