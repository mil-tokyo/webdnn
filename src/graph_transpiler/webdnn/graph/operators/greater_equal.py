from webdnn.graph.operators.elementwise import Elementwise


class GreaterEqual(Elementwise):
    """GreaterEqual(name)

    return 1 if x0 is greater than or equal to x1 elementwisely

    .. math::

        f(x) = x0 >= x1 ? 1 : 0;

    Signature
        .. code::

            y, = op(x0, x1)

        - **x0, x1** - Input variables.
        - **y** - Output variable.
    """
    pass
