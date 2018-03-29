from typing import Optional

from webdnn.graph.operators.pooling_2d import Pooling2D
from webdnn.graph.operators.util import IntOrTuple


class AveragePooling2D(Pooling2D):
    """AveragePooling2D(name, ksize, stride, padding, cover_all=True)

    Spatial average pooling operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.
        cover_all (bool, optional): If `True`, all input pixels are pooled into some output pixels.
        divide_without_padding: divides sum of input by the number of elements not of padding. Used in tensorflow.
        See https://github.com/mil-tokyo/webdnn/issues/694

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output value. Its order is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple,
                 cover_all: bool = True, divide_without_padding: bool = False):
        super(AveragePooling2D, self).__init__(name, ksize, stride, padding, cover_all)
        self.parameters["divide_without_padding"] = divide_without_padding
