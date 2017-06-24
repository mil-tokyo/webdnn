from functools import reduce
from typing import Iterable


def mul(iterable: Iterable, start=1, func=lambda x, y: x * y):
    return reduce(func, iterable, start)
