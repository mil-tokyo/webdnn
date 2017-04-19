from graph_builder.graph.operators.attributes import Attribute

"""
This attribute means data order, not number of dimensions
"""


class OrderNC(Attribute):
    """
    usage:
        Fully-Connected Input/Output.
    """
    pass


class OrderCN(Attribute):
    """
    usage:
        Fully-Connected Filter 
    """
    @staticmethod
    def convert_from(vars: Iterable[Variable]):
        pass


class OrderNHWC(Attribute):
    """
    usage:
        Convolution2D Input/Output of WebGPU
    """
    pass


class OrderHWNC(Attribute):
    """
    usage:
        Convolution2D Filter of WebGPU
    """
    pass


class OrderHWCN(Attribute):
    """
    usage:
        Fully-Connected Filter when Input variable is 4D.
    """
    pass


class OrderNCHW(Attribute):
    """
    usage:
        Chainer
    """
    pass
