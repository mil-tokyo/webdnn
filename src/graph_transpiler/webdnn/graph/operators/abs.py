from webdnn.graph.operators.elementwise import Elementwise


class Abs(Elementwise):
    """Abs(name)
    Elementwise absolute value operator.

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Absolute value of :code:`x`. Its shape and order is same as :code:`x0`.

        This operator also can be called by :func:`abs`.

        .. code::

            y = abs(x0)
    """
