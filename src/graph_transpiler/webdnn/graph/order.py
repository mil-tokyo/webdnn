from typing import Dict, List

from webdnn.graph.axis import Axis


class Order:
    """
    Class to represent variable data order

    attrs:
        ndim: number of dimensions
        axes: list of axis
        axes_dict: dictionary of pairs of axis and order index
    """
    ndim: int
    axes: List[Axis]
    axes_dict: Dict[Axis, int]

    def __init__(self, axes: List[Axis]):
        self.ndim = len(axes)
        self.axes = axes
        self.axes_dict = {a: i for i, a in enumerate(axes)}

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
