from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class Softplus(Elementwise):
    """Softplus(name, beta)

    Softplus operator.

    .. math::

        f(x) = \\frac{1}{beta} log(1 + exp(beta * x))

    Args:
        name (str): Operator name.
        beta (float): coefficient.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], beta: float):
        super().__init__(name)
        # FIXME: in most case, beta == 1.0. Separating case of beta == 1.0 may improve performance.
        self.parameters["beta"] = float(beta)
