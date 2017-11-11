from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


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
        y, = super(ConvertRGBAtoR, self).__call__(x0)
        ChannelMode.set(y, ChannelModeEnum.R)
        return y,

    def fold_constance(self, graph: Graph):
        x = self.inputs["x0"]  # type:ConstantVariable
        y = self.outputs["y"]  # type:Variable
        self.remove_all()
        OptimizeRule.replace_variable(graph, y, x.change_order(y.order))
        ChannelMode.set(x, ChannelModeEnum.R)


def convert_rgba_to_r(x: Variable):
    return ConvertRGBAtoR(None)(x)[0]
