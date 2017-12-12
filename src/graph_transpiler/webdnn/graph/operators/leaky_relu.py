from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class LeakyRelu(Elementwise):
    """LeakyRelu(name, slope)

    Leaky relu operator

    .. math::

        f(x) = max(x, ax)

    where :math:`a` is slope value.

    Args:
        slope (float): slope value

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], slope: float):
        super().__init__(name)
        self.parameters["slope"] = float(slope)
