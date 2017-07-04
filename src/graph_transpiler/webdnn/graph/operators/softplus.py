from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class Softplus(Elementwise):
    """Softplus activation

    log(1 + exp(beta * x)) / beta

    Args:
        name (str): Operator name.
        beta (float): coefficient.

    """

    def __init__(self, name: Optional[str], beta: float):
        super().__init__(name)
        # FIXME: in most case, beta == 1.0. Separating case of beta == 1.0 may improve performance.
        self.parameters["beta"] = float(beta)
