from typing import Optional

from webdnn.graph.operators.attributes.scalar_operation import ScalarOperation
from webdnn.graph.operators.elementwise import Elementwise


class ScalarAffine(Elementwise):
    """ScalarAffine(name, value)

    Affine transform operator with scalar scale and value

    Args:
        name (str): Operator name.
        scale (int or float): the scale value
        bias (int or float): the bias value

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.
    """

    def __init__(self, name: Optional[str], scale: float, bias: float):
        super().__init__(name)
        self.attributes.add(ScalarOperation(self))
        self.scale = float(scale)
        self.bias = float(bias)

    @property
    def scale(self) -> float:
        return self.parameters["scale"]

    @scale.setter
    def scale(self, value: float):
        self.parameters["scale"] = value

    @property
    def bias(self) -> float:
        return self.parameters["bias"]

    @bias.setter
    def bias(self, value: float):
        self.parameters["bias"] = value
