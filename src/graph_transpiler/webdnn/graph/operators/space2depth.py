from typing import Optional

from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operator import Operator
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


class Space2Depth(Operator):
    """Space2Depth(name, r)

    Space to depth transformation.

    Args:
        name (str): Operator name.
        r (int): Downscaling factor.
        spatial_axis1 (:class:`~Axis`): Axis which representing first spatial dimension
        spatial_axis2 (:class:`~Axis`): Axis which representing second spatial dimension
        depth_axis (:class:`~Axis`): Axis which representing depth dimension

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], r: int, spatial_axis1: Axis, spatial_axis2: Axis, depth_axis: Axis):
        super().__init__(name)
        self.parameters["r"] = int(r)
        self.parameters["spatial_axis1"] = spatial_axis1
        self.parameters["spatial_axis2"] = spatial_axis2
        self.parameters["depth_axis"] = depth_axis

    def __call__(self, x: Variable):
        for axis in [self.spatial_axis1, self.spatial_axis2, self.depth_axis]:
            assert axis in x.order.axes, f"""
[Space2Depth] Input variable "x" must has "spatial_axis1", "spatial_axis2", "depth_axis":
    (x) = {x}
    (spatial_axis1) = {self.spatial_axis1}
    (spatial_axis2) = {self.spatial_axis2}
    (depth_axis) = {self.depth_axis}
"""

        self.append_input("x", x)
        return self.exec()

    def exec(self):
        x = self.inputs["x"]

        assert x.shape_dict[self.spatial_axis1] % self.r == 0 and x.shape_dict[self.spatial_axis2] % self.r == 0, f"""
[Space2Depth] The size of spacial axes in input variable must be divisible by r:
    (x) = {x}
    (spacial axes) = {self.spatial_axis1, self.spatial_axis2} 
    (r) = {self.r}
"""

        y_shape_dict = AxisKeyDict(x.shape_dict)
        y_shape_dict[self.depth_axis] *= self.r * self.r
        y_shape_dict[self.spatial_axis1] //= self.r
        y_shape_dict[self.spatial_axis2] //= self.r

        y = Variable(list(y_shape_dict.values()), Order(list(y_shape_dict.keys())))
        self.append_output("y", y)
        return y,

    @property
    def r(self) -> int:
        return self.parameters["r"]

    @property
    def spatial_axis1(self) -> Axis:
        return self.parameters["spatial_axis1"]

    @property
    def spatial_axis2(self) -> Axis:
        return self.parameters["spatial_axis2"]

    @property
    def depth_axis(self) -> Axis:
        return self.parameters["depth_axis"]
