from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class ClippedRelu(Elementwise):
    """ClippedRelu(name, cap)

    Clipped relu operator.

    .. math::

        y = min(max(x, 0), cap)

    Args:
        name (str): Operator name.
        cap (float): clipping threshold.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], cap: float):
        super().__init__(name)
        self.parameters["cap"] = float(cap)
