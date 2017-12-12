from webdnn.graph.operators.elementwise import Elementwise


class Select(Elementwise):
    """GreaterEqual(name)

    return x1 if x0 is 1, otherwise x2.

    .. math::

        f(x) = x0 ? x1 : x2;

    Signature
        .. code::

            y, = op(x0, x1, x2)

        - **x0** - Condition variable.
        - **x1, x2** - Input variables.
        - **y** - Output variable.
    """
    pass
