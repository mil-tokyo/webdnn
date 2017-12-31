from typing import Dict, Type

_node_serial_counter_dict = {}  # type: Dict[Type[Node], int]


def _generate_name(node):
    klass = node.__class__
    if klass not in _node_serial_counter_dict:
        _node_serial_counter_dict[klass] = 0

    name = f"{klass.__name__}{_node_serial_counter_dict[klass]}"
    _node_serial_counter_dict[klass] += 1
    return name


class Node:
    """
    Basic graph node class.
    """

    def __init__(self, name=None):
        self.parameters = {}
        self.attributes = set()
        self.name = _generate_name(self) if name is None else name
        self._prevs = []
        self._nexts = []

    @property
    def prevs(self):
        return set(self._prevs)

    @property
    def nexts(self):
        return set(self._nexts)

    def append_prev(self, prev):
        # noinspection PyProtectedMember
        prev._nexts.append(self)
        self._prevs.append(prev)

    def remove_prev(self, prev):
        # noinspection PyProtectedMember
        prev._nexts.remove(self)
        self._prevs.remove(prev)

    def append_next(self, next):
        next.append_prev(self)

    def remove_next(self, next):
        next.remove_prev(self)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __str__(self):
        return self.__repr__()

    def get_attribute(self, Attr):
        return [attr for attr in self.attributes if isinstance(attr, Attr)]

    def has_attribute(self, Attr):
        return len(self.get_attribute(Attr)) > 0
