import numpy as np

from graph_builder.graph.axis import Axis
from graph_builder.graph.variable import Variable


def calculate_stride(var: Variable, axis: Axis):
    """
    行列の各次元のstride計算
    :param var: 
    :param axis: 
    :return: 
    """
    # noinspection PyTypeChecker
    return int(np.prod(var.shape[var.axis_order.axes_dict[axis] + 1:]))
