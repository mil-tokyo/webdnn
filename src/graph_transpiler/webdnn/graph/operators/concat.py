from typing import List, Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable


class Concat(Operator):
    """Concat(name, axis)

    Concatenate multiple variables into one variable along to specified axis.

    Args:
        name (str): Operator name.
        axis (:obj:~`webdnn.Axis`): target axis

    Signature
        .. code::

            y, = op(x0, x1, ...)

        - **x0**, **x1**, ... - Input variables. All variables has same shape except the specified axis.
        - **y** - Output variable. Its order is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis

    def __call__(self, *xs: Variable):
        axis = self.axis
        axis_index = xs[0].order.axes_dict[axis]
        axes = xs[0].order.axes

        y_shape = list(xs[0].shape)  # type: List[Placeholder]
        y_shape[axis_index] = 0

        for i, x in enumerate(xs):
            assert x.order.check_same_axes(xs[0].order), "Input variable of Concat operator must have same axes: " \
                                                         f"x0.order.axes={xs[0].order.axes}, x{i}.order.axes={xs[i].order.axes}"

            for other_axis in [other_axis for other_axis in axes if other_axis != axis]:
                if Placeholder.check_resolved(xs[0].shape_dict[other_axis]) and Placeholder.check_resolved(x.shape_dict[other_axis]):
                    assert xs[0].shape_dict[other_axis] == x.shape_dict[other_axis], "Input variable of Concat operator must be same " \
                                                                                     f"shape except the specified axis: " \
                                                                                     f"x0.shape_dict[{axis}]={xs[0].shape_dict[axis]}, " \
                                                                                     f"x{i}.shape_dict[{axis}]={xs[i].shape_dict[axis]}"

            self.append_input(f"x{i}", x)
            y_shape[axis_index] += x.shape_dict[axis]

        y = Variable(y_shape, xs[0].order)
        self.append_output("y", y)
        return y,

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]
