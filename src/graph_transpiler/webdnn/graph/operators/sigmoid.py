from webdnn.graph.operators.elementwise import Elementwise


class Sigmoid(Elementwise):
    """Sigmoid(name)

    Sigmoid operator.

    .. math::

        f(x) = \\frac{1}{1+exp(-x)}

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
