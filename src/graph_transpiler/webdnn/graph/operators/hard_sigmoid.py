from webdnn.graph.operators.elementwise import Elementwise


class HardSigmoid(Elementwise):
    """HardSigmoid(name)

    Hard sigmoid operator

    .. math::

        f(x) = \\left \\{ \\begin{array}{ll}
        0 & {\\rm if}~ x < -2.5 \\\\
        0.2 x + 0.5 & {\\rm if}~ -2.5 < x < 2.5 \\\\
        1 & {\\rm if}~ 2.5 < x.
        \\end{array} \\right.

    Args:
        name (str): Operator name.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """
