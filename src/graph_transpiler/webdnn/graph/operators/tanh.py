from webdnn.graph.operators.elementwise import Elementwise


class Tanh(Elementwise):
    """Tanh(name)

    Tanh operator.

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
