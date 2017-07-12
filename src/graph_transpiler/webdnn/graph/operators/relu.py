from webdnn.graph.operators.elementwise import Elementwise


class Relu(Elementwise):
    """Relu(name, slope)

    Rectified Linear Unit

    .. math::

        f(x) = max(0, x)

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
