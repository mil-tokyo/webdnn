from typing import Iterable, List

from graph_builder.graph.variable import Variable


class Graph:
    def __init__(self,
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable]):
        self.inputs: List[Variable] = list(inputs)
        self.outputs: List[Variable] = list(outputs)

    def __repr__(self):
        return f"""<{self.__class__.__name__} inputs={self.inputs}, outputs={self.outputs}>"""

    def __str__(self):
        return self.__repr__()
