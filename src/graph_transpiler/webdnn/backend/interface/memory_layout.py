from typing import Dict

import numpy as np

from webdnn.graph.variable import Variable


class IAllocation:
    variable: Variable
    offset: int

    @property
    def size(self) -> int:
        raise NotImplementedError()


class IMemoryLayout:
    size: int
    allocations: Dict[str, IAllocation]
    data: np.array

    @property
    def size(self) -> int:
        raise NotImplementedError()
