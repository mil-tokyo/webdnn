from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class ClippedRelu(Elementwise):
    """clipped relu activation

    min(max(x, 0), cap)

    Args:
        name (str): Operator name.
        cap (float): clipping threshold.

    """

    def __init__(self, name: Optional[str], cap: float):
        super().__init__(name)
        self.parameters["cap"] = float(cap)
