from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class ScalarPow(Elementwise):
    def __init__(self, name: Optional[str], value: float):
        super().__init__(name)
        self.parameters["value"] = float(value)

    @property
    def value(self) -> float:
        return self.parameters["value"]
