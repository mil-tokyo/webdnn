from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


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
        y, = super(ConvertRtoRGBA, self).__call__(x0)
        ChannelMode.set(y, ChannelModeEnum.RGBA)
        return y,

    def fold_constance(self):
        x = self.inputs["x0"]  # type:ConstantVariable
        y = self.outputs["y"]  # type:Variable
        self.remove_all()
        y.replace(x)
        ChannelMode.set(x, ChannelModeEnum.RGBA)
        x.change_order(y.order)


def convert_r_to_rgba(x: Variable):
    return ConvertRtoRGBA(None)(x)[0]
