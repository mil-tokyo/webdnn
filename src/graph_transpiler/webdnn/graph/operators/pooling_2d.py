from typing import Optional, Tuple

from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util import console


class Pooling2D(Operator):
    """Pooling2D(name, ksize, stride, padding)

    Spatial pooling base operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.

    Signature

        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output value. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple,
                 spatial_axis1: Axis, spatial_axis2: Axis):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)
        self.parameters["spatial_axis1"] = spatial_axis1
        self.parameters["spatial_axis2"] = spatial_axis2

        # FIXME: This constraints are only for cover_all=True mode.
        assert self.parameters["ksize"][0] >= self.parameters["stride"][0], \
            f"parameter \"ksize\" must be greater than or equal to parameter \"stride\":\n" \
            f"  (ksize[0]) = {self.parameters['ksize'][0]}\n" \
            f"  (stride[0]) = {self.parameters['stride'][0]}"

        assert self.parameters["ksize"][1] >= self.parameters["stride"][1], \
            f"parameter \"ksize\" must be greater than or equal to parameter \"stride\":\n" \
            f"  (ksize[1]) = {self.parameters['ksize'][1]}\n" \
            f"  (stride[1]) = {self.parameters['stride'][1]}"

    def __call__(self, x: Variable):
        for axis in [self.spatial_axis1, self.spatial_axis2]:
            assert axis in x.order.axes, f"""
[Pooling2D] Input variable "x" must has "spatial_axis1", "spatial_axis2":
    (x) = {x}
    (spatial_axis1) = {self.spatial_axis1}
    (spatial_axis2) = {self.spatial_axis2}
"""

        for axis in x.order.axes:
            if axis in [self.spatial_axis1, self.spatial_axis2]:
                continue

            self.attributes.add(Tensorwise(self, axis))

        self.append_input("x", x)
        return self.exec()

    def exec(self):
        x = self.inputs["x"]
        y_shape_dict = AxisKeyDict(x.shape_dict)
        y_shape_dict[self.spatial_axis1] = (x.shape_dict[self.spatial_axis1] + 2 * self.PH + self.SH - self.KH - 1) // self.SH + 1
        y_shape_dict[self.spatial_axis2] = (x.shape_dict[self.spatial_axis2] + 2 * self.PW + self.SW - self.KW - 1) // self.SW + 1

        if ((x.shape_dict[self.spatial_axis1] + 2 * self.PH - self.KH) % self.SH != 0) or \
            ((x.shape_dict[self.spatial_axis2] + 2 * self.PW - self.KW) % self.SW != 0):
            # https://github.com/fchollet/keras/issues/5090#issuecomment-279495401
            console.warning(
                "[Pooling2D] Performing pooling with parameters which causes edge is ignored. " +
                "Which edge (left / right) is ignored is different on frameworks," +
                " so slightly different result will be generated.")

        y = Variable(list(y_shape_dict.values()), Order(list(y_shape_dict.keys())))
        self.append_output("y", y)
        return y,

    @property
    def ksize(self) -> Tuple[int, int]:
        return self.parameters["ksize"]

    @property
    def stride(self) -> Tuple[int, int]:
        return self.parameters["stride"]

    @property
    def padding(self) -> Tuple[int, int]:
        return self.parameters["padding"]

    @property
    def KH(self) -> int:
        return self.ksize[0]

    @property
    def KW(self) -> int:
        return self.ksize[1]

    @property
    def SH(self) -> int:
        return self.stride[0]

    @property
    def SW(self) -> int:
        return self.stride[1]

    @property
    def PH(self) -> int:
        return self.padding[0]

    @property
    def PW(self) -> int:
        return self.padding[1]

    @property
    def spatial_axis1(self) -> Axis:
        return self.parameters["spatial_axis1"]

    @property
    def spatial_axis2(self) -> Axis:
        return self.parameters["spatial_axis2"]
