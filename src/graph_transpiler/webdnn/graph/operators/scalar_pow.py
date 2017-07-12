from typing import Optional

from webdnn.graph.operators.attributes.scalar_operation import ScalarOperation
from webdnn.graph.operators.elementwise import Elementwise


class ScalarPow(Elementwise):
    """ScalarPow(name, value)

    Elementwise power with scalar value

    Args:
        name (str): Operator name.
        value (int or float): the value

    Signature
        .. code::

            y, = op(x0)

        - **x0** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x0`.

        This operator also can be called by :code:`**`.

        .. code::

            y = x0 ** value
    """
    def __init__(self, name: Optional[str], value: float):
        super().__init__(name)
        self.attributes.add(ScalarOperation(self))
        self.parameters["value"] = float(value)

    @property
    def value(self) -> float:
        return self.parameters["value"]
