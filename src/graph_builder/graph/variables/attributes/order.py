from typing import Dict, Iterable, List

from graph_builder.graph.attribute import Attribute
from graph_builder.graph.graph import Variable
from graph_builder.graph.operators import attributes as A

"""
This attribute means data order, not number of dimensions
"""


class AxisOrder(Attribute):
    ndim: int
    axes: List[A.Axis]
    axis_dict: Dict[A.Axis, int]

    @classmethod
    def get_shape_dict(cls, var: Variable) -> Dict[A.Axis, int]:
        return dict(zip(cls.axes, var.shape))


class OrderC(AxisOrder):
    """
    usage:
        Bias Filter
    """
    ndim = 1
    axes = [A.Axis.C]
    axes_dict = {A.Axis.C: 0}


class OrderNC(AxisOrder):
    """
    usage:
        Fully-Connected Input/Output.
    """
    ndim = 2
    axes = [A.Axis.N, A.Axis.C]
    axes_dict = {A.Axis.N: 0, A.Axis.C: 1}


class OrderCN(AxisOrder):
    """
    usage:
        Fully-Connected Filter 
    """
    ndim = 2
    axes = [A.Axis.C, A.Axis.N]
    axes_dict = {A.Axis.C: 0, A.Axis.N: 1}

    @staticmethod
    def convert_from(vars: Iterable[Variable]):
        pass


class OrderNHWC(AxisOrder):
    """
    usage:
        Convolution2D Input/Output of WebGPU
    """
    ndim = 4
    axes = [A.Axis.N, A.Axis.H, A.Axis.W, A.Axis.C]
    axes_dict = {A.Axis.N: 0, A.Axis.H: 1, A.Axis.W: 2, A.Axis.C: 3}


class OrderHWNC(AxisOrder):
    """
    usage:
        Convolution2D Filter of WebGPU
    """
    ndim = 4
    axes = [A.Axis.H, A.Axis.W, A.Axis.N, A.Axis.C]
    axes_dict = {A.Axis.H: 0, A.Axis.W: 1, A.Axis.N: 2, A.Axis.C: 3}


class OrderHWCN(AxisOrder):
    """
    usage:
        Fully-Connected Filter when Input variable is 4D.
    """
    ndim = 4
    axes = [A.Axis.H, A.Axis.W, A.Axis.C, A.Axis.N]
    axes_dict = {A.Axis.H: 0, A.Axis.W: 1, A.Axis.C: 2, A.Axis.N: 3}


class OrderNCHW(AxisOrder):
    """
    usage:
        Chainer
    """
    ndim = 4
    axes = [A.Axis.N, A.Axis.C, A.Axis.H, A.Axis.W]
    axes_dict = {A.Axis.N: 0, A.Axis.C: 1, A.Axis.H: 2, A.Axis.W: 3}
