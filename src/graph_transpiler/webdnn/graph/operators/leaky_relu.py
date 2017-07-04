from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class LeakyRelu(Elementwise):
    """leaky relu activation

    max(x, slope*x)

    Args:
        name (str): Operator name.
        slope (float): slope in negative input.

    """

    def __init__(self, name: Optional[str], slope: float):
        super().__init__(name)
        self.parameters["slope"] = float(slope)
