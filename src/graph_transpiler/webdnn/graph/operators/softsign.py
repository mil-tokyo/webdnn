from webdnn.graph.operators.elementwise import Elementwise


class Softsign(Elementwise):
    """Softsign(name)

    Softsign operator.

    For more detail, see https://www.tensorflow.org/api_docs/python/tf/nn/softsign

    .. math::

        f(x) = \\frac{x}{abs(x) + 1}

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
