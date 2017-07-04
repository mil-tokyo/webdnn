from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class ThresholdRelu(Elementwise):
    """threshold relu activation

    f(x) = x > a ? x : 0

    Args:
        name (str): Operator name.
        threshold (float): threshold

    """

    def __init__(self, name: Optional[str], threshold: float):
        super().__init__(name)
        self.parameters["threshold"] = float(threshold)

    @property
    def threshold(self) -> float:
        return self.parameters["threshold"]
