from webdnn.graph.operators.pooling_2d import Pooling2D


class AveragePooling2D(Pooling2D):
    """AveragePooling2D(name, ksize, stride, padding, cover_all=True)

    Spatial average pooling operator.

    Args:
        name (str): Operator name.
        ksize (int or tuple of int): Kernel size.
        stride (int or tuple of int): Stride size.
        padding (int or tuple of int): Padding size.
        cover_all (bool, optional): If `True`, all input pixels are pooled into some output pixels.

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output value. Its order is same as :code:`x`.
    """
