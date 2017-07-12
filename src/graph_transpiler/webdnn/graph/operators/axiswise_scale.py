from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.axiswise import Axiswise
from webdnn.graph.operators.attributes.have_weights import HaveWeights
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.operators.attributes.post_axiswise import PostAxiswise
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable


class AxiswiseScale(Operator):
    """AxiswiseScale(name, axis)

    Multiply a scale value along to specified axis.

    Args:
        name (str): Operator name.
        axis (:obj:`~webdnn.Axis`): target axis

    Signature
        .. code::

            y, = op(x, s)

        - **x** - Data variable. It must has `axis` axis, and whose size must be same as :code:`s`.
        - **s** - Scale variable. It must be 1D variable and that size must be same as :code:`x.shape_dict[axis]`
        - **y** - Output variable. Its order and shape is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis
        self.attributes = {PostAxiswise(self, Axis.C),
                           Axiswise(self, Axis.C),
                           Inplace(self, "x", "y"),
                           HaveWeights(self)}

    def __call__(self, x: Variable, s: Variable):
        assert s.ndim == 1, f"Scale variable of AxiswiseScale operator should be 1D variable: s.ndim={s.ndim}"

        axis = self.axis
        if Placeholder.check_resolved(x.shape_dict[axis]) and Placeholder.check_resolved(s.size):
            assert x.shape_dict[axis] == s.size, f"Dimension mismatch: x.shape_dict[{axis}]={x.shape_dict[axis]}, " \
                                                 f"s.shape_dict[{axis}]={b.shape_dict[axis]}"

        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_input("s", s)
        self.append_output("y", y)
        return y,

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]
