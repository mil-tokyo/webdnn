from typing import List

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


class Concat(Operator):
    """Concatenate multiple variables into one variable along to specified axis.

    Args:
        name (str): Operator name.
        axis (:obj:~`graph_builder.graph.axis.Axis`): target axis
    """
    attributes = {PostElementwise,
                  PostAxiswise}

    def __init__(self, name: str, axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis

    def __call__(self, *xs: Variable):
        """
        Args:
            *xs (:class:`~graph_builder.graph.variable.Variable`): Inputs

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        concat_axis = self.parameters["axis"]  # type: int
        axis_index = xs[0].axis_order.axes_dict[concat_axis]
        axes_set = set(xs[0].axis_order.axes)

        y_shape = list(xs[0].shape)  # type: List[int]
        y_shape[axis_index] = 0

        for i, x in enumerate(xs):
            assert set(x.axis_order.axes) == axes_set
            for other_axis in [other_axis for other_axis in axes_set if other_axis != concat_axis]:
                assert xs[0].shape_dict[other_axis] == x.shape_dict[other_axis]

            self.append_input(f"x{i}", x)
            y_shape[axis_index] += x.shape_dict[concat_axis]

        y = Variable(y_shape, xs[0].axis_order)
        self.append_output("y", y)
        return y,
