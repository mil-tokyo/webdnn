from typing import TypeVar, Generic

from webdnn.graph import node

T = TypeVar("T", bound=node.Node)


class Attribute(Generic[T]):
    def __init__(self, base: T):
        self.base = base  # type: T

    def __str__(self):
        return self.__class__.__name__

    @classmethod
    def set(cls, base: T, kwargs):
        base.attributes.add(cls(base=base, **kwargs))
