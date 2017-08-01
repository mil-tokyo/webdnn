from webdnn.graph.operators.elementwise import Elementwise


class Exp(Elementwise):
    """Exp(name)

    Exponential operator.

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
