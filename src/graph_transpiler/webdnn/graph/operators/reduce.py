from abc import ABCMeta
from typing import Optional

from webdnn.graph import variable
from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.order import Order


class Reduce(Operator, metaclass=ABCMeta):
    """Reduce(name, axis)

    This operator reduces an axis into single element. This operator does NOT consider about the direction of reduction. For all axis
    without reduction axis, both input and output variables have same size.

    Args:
        name (str): Operator name.
        axis (:obj:`~webdnn.Axis`) axis which will be reduced.

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variables.
        - **y** - Output variable.
    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis

    def __call__(self, x: "variable.Variable"):
        reduced_axis = self.axis

        y_axes = list(x.order.axes)
        y_shape = [1 if axis == reduced_axis else x.shape_dict[axis] for axis in y_axes]
        y_order = Order(y_axes)

        y = variable.Variable(y_shape, y_order)

        for axis in x.order.axes:
            if axis != reduced_axis:
                self.attributes.add(Tensorwise(axis))

        self.append_input("x", x)
        self.append_output("y", y)
        return y,

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]
