from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.variable import Variable


class ConvertRGBAtoR(Elementwise):
    """ConvertRGBAtoR(name)
    Convert WebGL texture buffer channel mode from RGBA to R

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable whose channel mode is RGBA.
        - **y** - Output variable whose channel mode is R.
    """

    def __call__(self, x0: Variable):
        ys = super(ConvertRGBAtoR, self).__call__(x0)
        for y in ys:
            y.attributes.add(ChannelMode(y, ChannelModeEnum.R))
        return ys
