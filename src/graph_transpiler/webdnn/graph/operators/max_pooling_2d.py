from webdnn.graph.operators.pooling_2d import Pooling2D


class MaxPooling2D(Pooling2D):
    """MaxPooling2D(name, ksize, stride, padding)

    Spatial max pooling operator.

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
