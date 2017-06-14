from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.axiswise import Axiswise
from webdnn.graph.operators.attributes.have_weights import HaveWeights
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.operators.attributes.post_axiswise import PostAxiswise
from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable


class AxiswiseBias(Operator):
    """Adds a bias value along to specified axis.
    
    In general, after some operators such as :class:`~webdnn.graph.operators.linear.Linear` and 
    :class:`~webdnn.graph.operators.convolution2d.Convolution2D`, bias value are added.
    In that case, you should use this operator with axis parameter as :obj:`~webdnn.graph.axis.Axis.C`.

    Args:
        name (str): Operator name.
        axis (:obj:~`graph_transpiler.graph.axis.Axis`): target axis

    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis
        self.attributes = {PostAxiswise(self, axis),
                           Axiswise(self, axis),
                           Inplace(self, "x", "y"),
                           HaveWeights(self)}

    def __call__(self, x: Variable, b: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input
            b (:class:`~webdnn.graph.variable.Variable`): Bias value

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        assert b.ndim == 1
        if PlaceHolder.check_resolved(x.shape_dict[self.parameters["axis"]]) and PlaceHolder.check_resolved(b.size):
            assert x.shape_dict[self.parameters["axis"]] == b.size
        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_input("b", b)
        self.append_output("y", y)
        return y,

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]
