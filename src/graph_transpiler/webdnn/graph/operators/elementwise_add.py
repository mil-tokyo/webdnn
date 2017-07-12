from webdnn.graph.operators.elementwise import Elementwise


class ElementwiseAdd(Elementwise):
    """ElementwiseAdd(name)

    Elementwise add

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0, x1)

        - **x0**, **x1** - Input variable. They must be same shape.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.

        This operator also can be called by :code:`+`.

        .. code::

            y = x0 + x1
    """
