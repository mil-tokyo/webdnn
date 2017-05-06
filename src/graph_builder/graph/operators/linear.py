from typing import Optional

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNC


class Linear(Operator):
    """Fully connected operator.
    
    Output variable is 2D. The first dimension is same size as :obj:~`graph_builder.graph.Axis.N` 
    of input variable, and the second dimension is same size as :obj:~`graph_builder.graph.Axis.N`
    of weight variable.

    Args:
        name (str): Operator name.

    """
    attributes = {PostElementwise,
                  PostAxiswise,
                  HaveWeights}

    def __init__(self, name: Optional[str]):
        super().__init__(name)

    def __call__(self, x: Variable, w: Variable):
        """
        Args:
            x (:class:`~graph_builder.graph.variable.Variable`): Input
            w (:class:`~graph_builder.graph.variable.Variable`): Weight

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        self.append_input("x", x)
        self.append_input("w", w)

        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict
        assert x_shape_dict[Axis.C] == w_shape_dict[Axis.C]
        assert len(x_shape_dict) == len(w_shape_dict)
        if len(x_shape_dict) == 4:
            assert x_shape_dict[Axis.H] == w_shape_dict[Axis.H]
            assert x_shape_dict[Axis.W] == w_shape_dict[Axis.W]
        y = Variable([x_shape_dict[Axis.N], w_shape_dict[Axis.N]], OrderNC)
        self.append_output("y", y)
        return y,
