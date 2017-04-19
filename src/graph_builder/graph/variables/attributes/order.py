from typing import Dict, Set, List, Iterable
from graph_builder.graph import Variable
from graph_builder.graph.attribute import Attribute

"""
This attribute means data order, not number of dimensions
"""


class AxisOrder(Attribute):
    pass


class OrderC(AxisOrder):
    """
    usage:
        Bias Filter
    """
    ndim = 1
    order_chars = "C"

    @classmethod
    def get_shape_dict(cls, var: Variable) -> Dict[str, int]:
        return dict(zip(cls.order_chars, var.shape))


class OrderNC(AxisOrder):
    """
    usage:
        Fully-Connected Input/Output.
    """
    ndim = 2
    order_chars = "NC"

    @classmethod
    def get_shape_dict(cls, var: Variable) -> Dict[str, int]:
        return dict(zip(cls.order_chars, var.shape))


class OrderCN(AxisOrder):
    """
    usage:
        Fully-Connected Filter 
    """
    ndim = 2
    order_chars = "CN"

    @classmethod
    def get_shape_dict(cls, var: Variable) -> Dict[str, int]:
        return dict(zip(cls.order_chars, var.shape))

    @staticmethod
    def convert_from(vars: Iterable[Variable]):
        pass


class OrderNHWC(AxisOrder):
    """
    usage:
        Convolution2D Input/Output of WebGPU
    """
    ndim = 4
    order_chars = "NHWC"

    @classmethod
    def get_shape_dict(cls, var: Variable) -> Dict[str, int]:
        return dict(zip(cls.order_chars, var.shape))


class OrderHWNC(AxisOrder):
    """
    usage:
        Convolution2D Filter of WebGPU
    """
    ndim = 4
    order_chars = "HWNC"

    @classmethod
    def get_shape_dict(cls, var: Variable) -> Dict[str, int]:
        return dict(zip(cls.order_chars, var.shape))


class OrderHWCN(AxisOrder):
    """
    usage:
        Fully-Connected Filter when Input variable is 4D.
    """
    ndim = 4
    order_chars = "HWCN"

    @classmethod
    def get_shape_dict(cls, var: Variable) -> Dict[str, int]:
        return dict(zip(cls.order_chars, var.shape))


class OrderNCHW(AxisOrder):
    """
    usage:
        Chainer
    """
    ndim = 4
    order_chars = "NCHW"

    @classmethod
    def get_shape_dict(cls, var: Variable) -> Dict[str, int]:
        return dict(zip(cls.order_chars, var.shape))
