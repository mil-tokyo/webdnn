from webdnn.graph.operators.elementwise import Elementwise


class Rsqrt(Elementwise):
    """Rsqrt(name)

    Reciprocal of square root operator.

    .. math::

        f(x) = 1 / sqrt(x)

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
