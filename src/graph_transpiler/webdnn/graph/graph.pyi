from typing import Iterable, List

from webdnn.graph.variable import Variable

WEBDNN_LICENSE: str


class Graph:
    inputs: List[Variable]
    outputs: List[Variable]

    def __init__(self, inputs: Iterable[Variable], outputs: Iterable[Variable]): ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...
