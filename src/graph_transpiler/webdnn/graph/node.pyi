from typing import Dict, Set, Type, Optional, List, TypeVar

from webdnn.graph.attribute import Attribute

T_Attr = TypeVar("T_Attr", bound=Attribute)


class Node:
    name: str
    parameters: Dict[str, any]
    attributes: Set[Attribute]
    _prevs: List[Node]
    _nexts: List[Node]

    def __init__(self, name: Optional[str] = None): ...

    @property
    def prevs(self) -> Set[Node]: ...

    @property
    def nexts(self) -> Set[Node]: ...

    def append_prev(self, prev: Node): ...

    def remove_prev(self, prev: Node): ...

    def append_next(self, next: Node): ...

    def remove_next(self, next: Node): ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def get_attribute(self, Attr: Type[T_Attr]) -> List[T_Attr]: ...

    def has_attribute(self, Attr: Type[Attribute]) -> bool: ...
