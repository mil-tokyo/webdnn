from webdnn.graph.operators.reduce import Reduce


class ArgMax(Reduce):
    """ArgMax(name, axis)

    return index of maximum value along to specified axis

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
