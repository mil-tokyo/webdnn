from typing import Dict, Union

import numpy as np

from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable


class IAllocation:
    variable: Variable
    offset: int

    @property
    def size(self) -> int:
        raise NotImplementedError()


class IMemoryLayout:
    size: Union[int, PlaceHolder]
    allocations: Dict[str, IAllocation]
    data: np.array

    @property
    def size(self) -> Union[int, PlaceHolder]:
        raise NotImplementedError()

    @size.setter
    def size(self, size: Union[int, PlaceHolder]):
        raise NotImplementedError
