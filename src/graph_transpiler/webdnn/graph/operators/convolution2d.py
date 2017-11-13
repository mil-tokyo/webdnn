from typing import Tuple, Optional

from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operator import Operator
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


class Convolution2D(Operator):
    """Convolution2D(name, ksize, stride, padding, dilation_rate=1)

    Spatial convolution operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.
        spatial_axis1 (:class:`~Axis`): Axis which representing first spatial dimension
        spatial_axis2 (:class:`~Axis`): Axis which representing second spatial dimension
        kernel_axis1 (:class:`~Axis`): Axis which representing first kernel dimension
        kernel_axis2 (:class:`~Axis`): Axis which representing second kernel dimension
        channel_axis (:class:`~Axis`): Axis which representing channel dimension
        dilation_rate (int or tuple of int): Dilation rate. 1 means ordinary convolution.
         Input pixels are shifted by (dilation_rate - 1) pixels.

    Signature
        .. code::

            y, = op(x, w)

        - **x** - Input variables. It must has 3 axes, :code:`spatial_axis1`, :code:`spatial_axis2`, and  :code:`channel_axis`.
        - **w** - Kernel variables. It must has 3 axes, :code:`kernel_axis1`, :code:`kernel_axis2`, and  :code:`channel_axis`. Its size of
            :code:`channel_axis` must be same as :code:`x`
        - **y** - Output variable. Its has all axes of `x` and `w`, without `kernel_axis1`, `kernel_axis2`, and `channel_axis`.
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple,
                 spatial_axis1: Axis, spatial_axis2: Axis, kernel_axis1: Axis, kernel_axis2: Axis, channel_axis: Axis,
                 dilation_rate: Optional[IntOrTuple] = 1):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)
        self.parameters["dilation_rate"] = to_tuple(dilation_rate)
        self.parameters["spatial_axis1"] = spatial_axis1
        self.parameters["spatial_axis2"] = spatial_axis2
        self.parameters["kernel_axis1"] = kernel_axis1
        self.parameters["kernel_axis2"] = kernel_axis2
        self.parameters["channel_axis"] = channel_axis

    def __call__(self, x: Variable, w: Variable) -> Tuple[Variable]:
        for axis in [self.spatial_axis1, self.spatial_axis2, self.channel_axis]:
            assert axis in x.order.axes, f"""
[Convolution2D] Input variable "x" must has "spatial_axis1", "spatial_axis2", "channel_axis":
    (x) = {x}
    (spatial_axis1) = {self.spatial_axis1}
    (spatial_axis2) = {self.spatial_axis2}
    (channel_axis) = {self.channel_axis}
"""

        for axis in [self.kernel_axis1, self.kernel_axis2, self.channel_axis]:
            assert axis in w.order.axes, f"""
[Convolution2D] Input variable "w" must has "kernel_axis1", "kernel_axis2", "channel_axis":
    (w) = {w}
    (kernel_axis1) = {self.kernel_axis1}
    (kernel_axis2) = {self.kernel_axis2}
    (channel_axis) = {self.channel_axis}
"""

        assert x.shape_dict[self.channel_axis] == w.shape_dict[self.channel_axis], f"""
[Convolution2D] Channel size mismatch:
    (x[channel_axis]) = {x.shape_dict[self.channel_axis]}
    (w[channel_axis]) = {w.shape_dict[self.channel_axis]}
"""

        assert w.shape_dict[self.kernel_axis1] == self.KH and w.shape_dict[self.kernel_axis2] == self.KW, f"""
[Convolution2D] Kernel size mismatch:
    (w[kernel_axis1]) = {w.shape_dict[self.kernel_axis1]}
    (w[kernel_axis2]) = {w.shape_dict[self.kernel_axis2]}
    (KH) = {self.KH}
    (KW) = {self.KW}
"""

        for axis in x.order.axes:
            if axis not in [self.spatial_axis1, self.spatial_axis2, self.channel_axis]:
                assert axis in [self.kernel_axis1, self.kernel_axis2] or axis not in w.order.axes, f"""
[Convolution2D] Axis is duplicated:
    (x) = {x}
    (w) = {w}
    (duplicated axis) = {axis}
"""

        for axis in w.order.axes:
            if axis not in [self.kernel_axis1, self.kernel_axis2, self.channel_axis]:
                assert axis in [self.spatial_axis1, self.spatial_axis2] or axis not in w.order.axes, f"""
[Convolution2D] Axis is duplicated:
    (x) = {x}
    (w) = {w}
    (duplicated axis) = {axis}
"""

        self.append_input("x", x)
        self.append_input("w", w)
        return self.exec()

    def exec(self):
        x = self.inputs["x"]
        w = self.inputs["w"]

        y_shape_dict = AxisKeyDict(x.shape_dict)
        y_shape_dict[self.spatial_axis1] = (x.shape_dict[self.spatial_axis1] + 2 * self.PH - self.WH) // self.SH + 1
        y_shape_dict[self.spatial_axis2] = (x.shape_dict[self.spatial_axis2] + 2 * self.PW - self.WW) // self.SW + 1
        del y_shape_dict[self.channel_axis]
        for axis in w.order.axes:
            if axis not in [self.kernel_axis1, self.kernel_axis2, self.channel_axis]:
                y_shape_dict[axis] = w.shape_dict[axis]

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
    def dilation_rate(self) -> Tuple[int, int]:
        return self.parameters["dilation_rate"]

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
    def DH(self) -> int:
        return self.dilation_rate[0]

    @property
    def DW(self) -> int:
        return self.dilation_rate[1]

    @property
    def WH(self) -> int:
        return self.DH * (self.KH - 1) + 1

    @property
    def WW(self) -> int:
        return self.DW * (self.KW - 1) + 1

    @property
    def spatial_axis1(self) -> Axis:
        return self.parameters["spatial_axis1"]

    @property
    def spatial_axis2(self) -> Axis:
        return self.parameters["spatial_axis2"]

    @property
    def kernel_axis1(self) -> Axis:
        return self.parameters["kernel_axis1"]

    @property
    def kernel_axis2(self) -> Axis:
        return self.parameters["kernel_axis2"]

    @property
    def channel_axis(self) -> Axis:
        return self.parameters["channel_axis"]
