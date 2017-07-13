from webdnn.graph.operators.elementwise import Elementwise


class ElementwiseAddRelu(Elementwise):
    """Relu(name, slope)

    ElementwiseAdd + ReLU

    .. math::

        f(x) = max(0, x0 + x1)

    Signature
        .. code::

            y, = op(x0, x1)

        - **x0, x1** - Input variables.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
