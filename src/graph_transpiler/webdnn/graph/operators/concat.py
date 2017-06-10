from typing import List, Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise
from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable


class Concat(Operator):
    """Concatenate multiple variables into one variable along to specified axis.

    Args:
        name (str): Operator name.
        axis (:obj:~`graph_transpiler.graph.axis.Axis`): target axis
    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis
        self.attributes = {Elementwise(self)}

    def __call__(self, *xs: Variable):
        """
        Args:
            *xs (:class:`~webdnn.graph.variable.Variable`): Inputs

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        concat_axis = self.parameters["axis"]  # type: Axis
        axis_index = xs[0].order.axes_dict[concat_axis]
        axes_set = set(xs[0].order.axes)

        y_shape = list(xs[0].shape)  # type: List[PlaceHolder]
        y_shape[axis_index] = 0

        for i, x in enumerate(xs):
            assert set(x.order.axes) == axes_set
            for other_axis in [other_axis for other_axis in axes_set if other_axis != concat_axis]:
                assert xs[0].shape_dict[other_axis] == x.shape_dict[other_axis]

            self.append_input(f"x{i}", x)
            y_shape[axis_index] += x.shape_dict[concat_axis]

        y = Variable(y_shape, xs[0].order)
        self.append_output("y", y)
        return y,

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]
