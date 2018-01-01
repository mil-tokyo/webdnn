from typing import Optional

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.graph import variable
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


class ConvertRtoRGBA(Operator):
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

    def __init__(self, name: Optional[str]):
        super().__init__(name)

    def __call__(self, *xs: "variable.Variable"):
        y_axes = []
        y_shape_dict = AxisKeyDict()

        # Check variable in descent order of the number of dimensions.
        # Without this procedure, in case that x0.order=C and x1.order=NC, the output order is CN. Expected result is NC.
        xs_order = [(i, x) for i, x in enumerate(xs)]
        xs_order.sort(key=lambda d: d[1].ndim, reverse=True)

        for i, x in xs_order:
            for axis in x.order.axes:
                if axis in y_axes:
                    if y_shape_dict[axis] == 1:
                        # broadcast
                        y_shape_dict[axis] = x.shape_dict[axis]
                else:
                    y_axes.append(axis)
                    y_shape_dict[axis] = x.shape_dict[axis]

                if Placeholder.check_resolved(x.shape_dict[axis]):
                    if Placeholder.check_resolved(y_shape_dict[axis]):
                        assert y_shape_dict[axis] == x.shape_dict[axis] or x.shape_dict[axis] == 1, \
                            "All input variables of elementwise operator should be same shape: " \
                            f"y.shape_dict[{axis}]={y_shape_dict[axis]}, " \
                            f"x{i}.shape_dict[{axis}]={x.shape_dict[axis]}"
                    else:
                        y_shape_dict[axis] = x.shape_dict[axis]

        y = variable.Variable([y_shape_dict[axis] for axis in y_axes], Order(y_axes))
        ChannelMode.set(y, ChannelModeEnum.RGBA)

        for i, x in enumerate(xs):
            self.append_input(f"x{i}", x)
        self.append_output("y", y)
        return y,

    def fold_constance(self, graph: Graph):
        x = self.inputs["x0"]  # type: ConstantVariable
        y = self.outputs["y"]  # type: Variable
        self.remove_all()
        OptimizeRule.replace_variable(graph, y, x.change_order(y.order))
        ChannelMode.set(x, ChannelModeEnum.RGBA)


def convert_r_to_rgba(x: Variable):
    return ConvertRtoRGBA(None)(x)[0]
