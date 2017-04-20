from typing import List, Type
import numpy as np

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA


def calculate_stride(var: Variable, axis: A.Axis):
    """
    行列の各次元のstride計算
    :param var: 
    :param axis: 
    :return: 
    """
    return int(np.prod(var.shape[var.axis_order.axes_dict[axis] + 1:]))
