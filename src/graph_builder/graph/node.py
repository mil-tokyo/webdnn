from typing import Dict, Set, Type

from graph_builder.graph.attribute import Attribute


class Node:
    attributes: Set[Type[Attribute]] = set()
    parameters: Dict[str, any]

    def __init__(self, parameters: Dict[str, any] = None):
        self.parameters = parameters if parameters is not None else {}
        self.attributes = set(self.attributes)  # copy construction

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __str__(self):
        return self.__repr__()
