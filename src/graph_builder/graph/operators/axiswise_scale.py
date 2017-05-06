from typing import Optional

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.axiswise import Axiswise
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


class AxiswiseScale(Operator):
    """Multiply a scale value along to specified axis.

    This is scale version of :class:`~graph_builder.graph.operators.axiswise_bias.AxiswiseBias`. Please see that.

    Args:
        name (str): Operator name.
        axis (:obj:~`graph_builder.graph.axis.Axis`): target axis

    """
    attributes = {PostElementwise,
                  PostAxiswise,
                  Axiswise,
                  Inplace,
                  HaveWeights}

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis

    def __call__(self, x: Variable, s: Variable):
        """
        Args:
            x (:class:`~graph_builder.graph.variable.Variable`): Input
            s (:class:`~graph_builder.graph.variable.Variable`): Scale value

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        assert s.ndim == 1
        assert x.shape_dict[self.parameters["axis"]] == s.size
        y = Variable(x.shape, x.axis_order)
        self.append_input("x", x)
        self.append_input("s", s)
        self.append_output("y", y)
        return y,
