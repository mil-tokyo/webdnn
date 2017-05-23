from typing import Dict

from webdnn.graph.variable import Variable


class IAllocation:
    variable: Variable
    offset: int

    @property
    def size(self) -> int:
        raise NotImplementedError()


class IMemoryLayout:
    size: int
    __dict__: Dict[str, IAllocation]

    @property
    def size(self) -> int:
        raise NotImplementedError()
