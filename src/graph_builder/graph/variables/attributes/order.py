from typing import Dict, List, ClassVar

from graph_builder.graph.attribute import Attribute
from graph_builder.graph.axis import Axis

"""
This attribute means data order, not number of dimensions
"""


class AxisOrder(Attribute):
    ndim: ClassVar[int]
    axes: ClassVar[List[Axis]]
    axes_dict: ClassVar[Dict[Axis, int]]


class OrderC(AxisOrder):
    """
    usage:
        Bias Filter
    """
    ndim = 1
    axes = [Axis.C]
    axes_dict = {Axis.C: 0}


class OrderNC(AxisOrder):
    """
    usage:
        Fully-Connected Input/Output.
    """
    ndim = 2
    axes = [Axis.N, Axis.C]
    axes_dict = {Axis.N: 0, Axis.C: 1}


class OrderCN(AxisOrder):
    """
    usage:
        Fully-Connected Filter 
    """
    ndim = 2
    axes = [Axis.C, Axis.N]
    axes_dict = {Axis.C: 0, Axis.N: 1}


class OrderNHWC(AxisOrder):
    """
    usage:
        Convolution2D Input/Output of WebGPU
    """
    ndim = 4
    axes = [Axis.N, Axis.H, Axis.W, Axis.C]
    axes_dict = {Axis.N: 0, Axis.H: 1, Axis.W: 2, Axis.C: 3}


class OrderHWNC(AxisOrder):
    """
    usage:
        Convolution2D Filter of WebGPU
    """
    ndim = 4
    axes = [Axis.H, Axis.W, Axis.N, Axis.C]
    axes_dict = {Axis.H: 0, Axis.W: 1, Axis.N: 2, Axis.C: 3}


class OrderHWCN(AxisOrder):
    """
    usage:
        Fully-Connected Filter when Input variable is 4D.
    """
    ndim = 4
    axes = [Axis.H, Axis.W, Axis.C, Axis.N]
    axes_dict = {Axis.H: 0, Axis.W: 1, Axis.C: 2, Axis.N: 3}


class OrderNCHW(AxisOrder):
    """
    usage:
        Chainer
    """
    ndim = 4
    axes = [Axis.N, Axis.C, Axis.H, Axis.W]
    axes_dict = {Axis.N: 0, Axis.C: 1, Axis.H: 2, Axis.W: 3}


class OrderCNHW(AxisOrder):
    """
    usage:
        Chainer Deconvolution2D Filter
    """
    ndim = 4
    axes = [Axis.C, Axis.N, Axis.H, Axis.W]
    axes_dict = {Axis.N: 1, Axis.C: 0, Axis.H: 2, Axis.W: 3}


class OrderCHWN(AxisOrder):
    """
    """
    ndim = 4
    axes = [Axis.C, Axis.H, Axis.W, Axis.N]
    axes_dict = {Axis.N: 3, Axis.C: 0, Axis.H: 1, Axis.W: 2}
