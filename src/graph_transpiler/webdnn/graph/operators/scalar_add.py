from typing import Optional

from webdnn.graph.operators.elementwise import Elementwise


class ScalarAdd(Elementwise):
    def __init__(self, name: Optional[str], value: float):
        super().__init__(name)
        self.parameters["value"] = value

    @property
    def value(self) -> float:
        return self.parameters["value"]
