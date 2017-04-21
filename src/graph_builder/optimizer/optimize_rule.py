from abc import abstractmethod
from typing import Tuple

from graph_builder.graph.operator import Operator


class OptimizeRule:
    @abstractmethod
    def __call__(self, graph: Operator) -> Tuple[Operator, bool]:
        raise NotImplementedError(f"Optimize rule '{self.__class__.__name__}' is not implemented yet.")
