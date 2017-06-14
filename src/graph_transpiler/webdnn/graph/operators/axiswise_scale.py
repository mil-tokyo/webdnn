from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.axiswise import Axiswise
from webdnn.graph.operators.attributes.have_weights import HaveWeights
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.operators.attributes.post_axiswise import PostAxiswise
from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable


class AxiswiseScale(Operator):
    """Multiply a scale value along to specified axis.

    This is scale version of :class:`~webdnn.graph.operators.axiswise_bias.AxiswiseBias`. Please see that.

    Args:
        name (str): Operator name.
        axis (:obj:~`graph_transpiler.graph.axis.Axis`): target axis

    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis
        self.attributes = {PostAxiswise(self, Axis.C),
                           Axiswise(self, Axis.C),
                           Inplace(self, "x", "y"),
                           HaveWeights(self)}

    def __call__(self, x: Variable, s: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input
            s (:class:`~webdnn.graph.variable.Variable`): Scale value

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        assert s.ndim == 1
        if PlaceHolder.check_resolved(x.shape_dict[self.parameters["axis"]]) and PlaceHolder.check_resolved(s.size):
            assert x.shape_dict[self.parameters["axis"]] == s.size
        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_input("s", s)
        self.append_output("y", y)
        return y,

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]
