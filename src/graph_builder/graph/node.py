from typing import Dict, Set, Type

from graph_builder.graph.attribute import Attribute


class Node:
    attributes: Set[Type[Attribute]] = set()
    parameters: Dict[str, any]
    prevs: Set["Node"]
    nexts: Set["Node"]

    def __init__(self, parameters: Dict[str, any] = None):
        self.parameters = parameters if parameters is not None else {}
        self.attributes = set(self.attributes)  # copy construction
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
