from typing import Dict, List

from webdnn.graph.axis import Axis


class Order:
    """Order(axes)

    Descriptor class for representing semantics of data order.

    For example, :obj:`~webdnn.graph.order.OrderNHWC` means that the data is aligned as Channel-major (Batch-size-minor).
    Popular data order is already defined in :mod:`webdnn.graph.order`. You should use pre-defined order instance.

    If you have to define new data order, you can simply as follows.

    .. code::

        OrderHCNW = Order([Axis.H, Axis.C, Axis.N, Axis.W])

    Args:
        axes(list of :class:`~webdnn.Axis`): list of axis.

    Attributes:
        ndim(int): number of dimensions
        axes(list of :class:`~webdnn.Axis`): list of axis
        axes_dict(dict of :class:`~webdnn.Axis` and int): dictionary of pairs of axis and order index
    """

    def __init__(self, axes: List[Axis]):
        self.ndim = len(axes)  # type: int
        self.axes = axes  # type: List[Axis]
        self.axes_dict = {a: i for i, a in enumerate(axes)}  # type: Dict[Axis, int]

    def __eq__(self, other):
        if isinstance(other, Order):
            return self.axes == other.axes

        else:
            return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "".join([axis.name for axis in self.axes])


"""
usage:
    Bias Filter
"""
OrderC = Order([Axis.C])

"""
usage:
    Fully-Connected Input/Output.
"""
OrderNC = Order([Axis.N, Axis.C])

"""
usage:
    Fully-Connected Filter 
"""
OrderCN = Order([Axis.C, Axis.N])

"""
usage:
    Convolution2D Input/Output of WebGPU
"""
OrderNHWC = Order([Axis.N, Axis.H, Axis.W, Axis.C])

"""
usage:
    Convolution2D Filter of WebGPU
"""
OrderHWNC = Order([Axis.H, Axis.W, Axis.N, Axis.C])

"""
usage:
    Fully-Connected Filter when Input variable is 4D.
"""
OrderHWCN = Order([Axis.H, Axis.W, Axis.C, Axis.N])

"""
usage:
    Chainer
"""
OrderNCHW = Order([Axis.N, Axis.C, Axis.H, Axis.W])

"""
usage:
    Chainer Deconvolution2D Filter
"""
OrderCNHW = Order([Axis.C, Axis.N, Axis.H, Axis.W])

"""
usage:
    Chainer Deconvolution2D Filter
"""
OrderCHWN = Order([Axis.C, Axis.H, Axis.W, Axis.N])

OrderNT = Order([Axis.N, Axis.T])
OrderNTC = Order([Axis.N, Axis.T, Axis.C])
