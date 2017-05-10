from typing import Optional

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.axiswise import Axiswise
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


class AxiswiseBias(Operator):
    """Adds a bias value along to specified axis.
    
    In general, after some operators such as :class:`~graph_builder.graph.operators.linear.Linear` and 
    :class:`~graph_builder.graph.operators.convolution2d.Convolution2D`, bias value are added.
    In that case, you should use this operator with axis parameter as :obj:`~graph_builder.graph.axis.Axis.C`.

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

    def __call__(self, x: Variable, b: Variable):
        """
        Args:
            x (:class:`~graph_builder.graph.variable.Variable`): Input
            b (:class:`~graph_builder.graph.variable.Variable`): Bias value

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        assert b.ndim == 1
        assert x.shape_dict[self.parameters["axis"]] == b.size
        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_input("b", b)
        self.append_output("y", y)
        return y,
