from typing import Dict, Set, Type, Optional

from graph_transpiler.graph.interface import IAttribute, INode

_node_serial_counter_dict: Dict[Type["Node"], int] = {}


def _generate_name(node: "Node"):
    klass = node.__class__
    if klass not in _node_serial_counter_dict:
        _node_serial_counter_dict[klass] = 0

    name = f"{klass.__name__}{_node_serial_counter_dict[klass]}"
    _node_serial_counter_dict[klass] += 1
    return name


class Node(INode):
    attributes: Set[IAttribute]
    parameters: Dict[str, any]
    prevs: Set["Node"]
    nexts: Set["Node"]

    def __init__(self, name: Optional[str] = None):
        if name is None:
            name = _generate_name(self)
        self.parameters = {}
        self.attributes = set()
        self.name = name
        self.prevs = set()
        self.nexts = set()

    def append_prev(self, prev: "Node"):
        prev.nexts.add(self)
        self.prevs.add(prev)

    def remove_prev(self, prev: "Node"):
        prev.nexts.remove(self)
        self.prevs.remove(prev)

    def append_next(self, next: "Node"):
        next.append_prev(self)

    def remove_next(self, next: "Node"):
        next.remove_prev(self)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __str__(self):
        return self.__repr__()
