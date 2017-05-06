from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


class ElementwiseSum(Operator):
    """Calculate elementwise sum of multiple input variables.

    Args:
        name (str): Operator name.
    """
    attributes = {PostElementwise,
                  PostAxiswise}

    def __init__(self, name: str):
        super().__init__(name)

    def __call__(self, *xs: Variable):
        """
        Args:
            *xs (:class:`~graph_builder.graph.variable.Variable`): Inputs

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        y = Variable(xs[0].shape, xs[0].axis_order)
        for i, x in enumerate(xs):
            for axis in x.axis_order.axes:
                assert axis in y.axis_order.axes and y.shape_dict[axis] == x.shape_dict[axis]

            self.append_input(f"x{i}", x)
        self.append_output("y", y)
        return y,
