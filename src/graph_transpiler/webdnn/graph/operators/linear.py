from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.have_weights import HaveWeights
from webdnn.graph.operators.attributes.post_axiswise import PostAxiswise
from webdnn.graph.order import OrderNC
from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable


class Linear(Operator):
    """Fully connected operator.
    
    Output variable is 2D. The first dimension is same size as :obj:~`graph_transpiler.graph.Axis.N` 
    of input variable, and the second dimension is same size as :obj:~`graph_transpiler.graph.Axis.N`
    of weight variable.

    Args:
        name (str): Operator name.

    """

    def __init__(self, name: Optional[str]):
        super().__init__(name)
        self.attributes = {PostAxiswise(self, Axis.C),
                           HaveWeights(self)}

    def __call__(self, x: Variable, w: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input
            w (:class:`~webdnn.graph.variable.Variable`): Weight

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        self.append_input("x", x)
        self.append_input("w", w)

        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict
        if PlaceHolder.check_resolved(x_shape_dict[Axis.C]) and PlaceHolder.check_resolved(w_shape_dict[Axis.C]):
            assert x_shape_dict[Axis.C] == w_shape_dict[Axis.C]
        assert len(x_shape_dict) == len(w_shape_dict)
        if len(x_shape_dict) == 4:
            if PlaceHolder.check_resolved(x_shape_dict[Axis.H]) and PlaceHolder.check_resolved(w_shape_dict[Axis.H]):
                assert x_shape_dict[Axis.H] == w_shape_dict[Axis.H]
            if PlaceHolder.check_resolved(x_shape_dict[Axis.W]) and PlaceHolder.check_resolved(w_shape_dict[Axis.W]):
                assert x_shape_dict[Axis.W] == w_shape_dict[Axis.W]
        y = Variable([x_shape_dict[Axis.N], w_shape_dict[Axis.N]], OrderNC)
        self.append_output("y", y)
        return y,
