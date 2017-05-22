from collections import Collection
from typing import Union, Tuple


def to_tuple(x, length=2):
    if isinstance(x, Collection):
        assert len(x) == length
        return tuple(x)

    else:
        return (x,) * length


IntOrTuple = Union['IntOrTuple', int, Tuple[int, int]]
