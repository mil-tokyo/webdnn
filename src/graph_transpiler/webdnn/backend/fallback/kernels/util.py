from typing import Union

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable


def calculate_stride(var: Variable, axis: Axis) -> Union[int, Placeholder]:
    """
    calculate stride for specified dimension of specified variable.

    :param var: variable
    :param axis: axis
    :return: 
    """
    return np.product(var.shape[var.order.axes_dict[axis] + 1:])
