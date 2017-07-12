from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class ThresholdRelu(Elementwise):
    """ThresholdRelu(name)

    Relu operator with threshold.

    .. math::

        f(x) = x > a ? x : 0

    Args:
        name (str): Operator name.
        threshold (float): the threshold value.

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], threshold: float):
        super().__init__(name)
        self.parameters["threshold"] = float(threshold)

    @property
    def threshold(self) -> float:
        return self.parameters["threshold"]
