from typing import Dict, Set, Type, Optional, List, TypeVar

from webdnn.graph import attribute

_node_serial_counter_dict = {}  # type: Dict[Type[Node], int]


def _generate_name(node: "Node"):
    klass = node.__class__
    if klass not in _node_serial_counter_dict:
        _node_serial_counter_dict[klass] = 0

    name = f"{klass.__name__}{_node_serial_counter_dict[klass]}"
    _node_serial_counter_dict[klass] += 1
    return name


_TAttr = TypeVar("T", bound="attribute.Attribute")


class Node:
    """
    Basic graph node class.
    """

    def __init__(self, name: Optional[str] = None):
        if name is None:
            name = _generate_name(self)
        self.parameters = {}  # type: Dict[str, any]
        self.attributes = set()  # type: Set[attribute.Attribute]
        self.name = name
        self._prevs = []  # type: List[Node]
        self._nexts = []  # type: List[Node]

    @property
    def prevs(self) -> Set["Node"]:
        return set(self._prevs)

    @property
    def nexts(self) -> Set["Node"]:
        return set(self._nexts)

    def append_prev(self, prev: "Node"):
        prev._nexts.append(self)
        self._prevs.append(prev)

    def remove_prev(self, prev: "Node"):
        prev._nexts.remove(self)
        self._prevs.remove(prev)

    def append_next(self, next: "Node"):
        next.append_prev(self)

    def remove_next(self, next: "Node"):
        next.remove_prev(self)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __str__(self):
        return self.__repr__()

    def get_attribute(self, Attr: Type[_TAttr]) -> List[_TAttr]:
        return [attr for attr in self.attributes if isinstance(attr, Attr)]

    def has_attribute(self, Attr: Type["attribute.Attribute"]) -> bool:
        return len(self.get_attribute(Attr)) > 0
