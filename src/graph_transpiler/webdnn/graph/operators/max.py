from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operators.reduce import Reduce


class Max(Reduce):
    """Max(name, axis)

    return elements of maximum value along to specified axis

    Args:
        name (str) : Operator name.
        axis (:obj:`~webdnn.graph.axis.Axis`) : axis which will be reduced.

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variables.
        - **y** - Output variable.
    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name, axis=axis)
