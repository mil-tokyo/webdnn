from webdnn.graph.operators.elementwise import Elementwise


class Elu(Elementwise):
    """Elu(name)

    Exponential Linear Unit operator.

    .. math::

        f(x) = \\left \\{ \\begin{array}{ll}
        x & {\\rm if}~ x \\ge 0 \\\\
        \\exp(x) - 1 & {\\rm if}~ x < 0,
        \\end{array} \\right.

    More detail, please see https://arxiv.org/abs/1511.07289

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
