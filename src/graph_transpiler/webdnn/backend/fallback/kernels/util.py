import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.variable import Variable


def calculate_stride(var: Variable, axis: Axis):
    """
    行列の各次元のstride計算
    :param var: 
    :param axis: 
    :return: 
    """
    # noinspection PyTypeChecker
    return int(np.prod(var.shape[var.order.axes_dict[axis] + 1:]))
