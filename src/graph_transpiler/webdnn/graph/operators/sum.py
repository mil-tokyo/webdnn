from webdnn.graph.operators.reduce import Reduce


class Sum(Reduce):
    """Sum(name, axis)

    return sum of the input tensor along to specified axis

    Args:
        name (str): Operator name.
        axis (:obj:`~webdnn.Axis`) axis which will be reduced.

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variables.
        - **y** - Output variable.
    """
    pass
