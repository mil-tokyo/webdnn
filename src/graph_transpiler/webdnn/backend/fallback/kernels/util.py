from typing import Union

from webdnn.graph.axis import Axis
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul


def calculate_stride(var: Variable, axis: Axis) -> Union[int, Placeholder]:
    """
    calculate stride for specified dimension of specified variable.

    :param var: variable
    :param axis: axis
    :return:
    """
    return mul(var.shape[var.order.axes_dict[axis] + 1:])
