from typing import Dict

from graph_builder.graph.variable import Variable


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
