from abc import abstractmethod

from graph_builder.graph import Operator


class OptimizeRule:
    @abstractmethod
    def optimize(self, graph: Operator) -> Operator:
        raise NotImplementedError(f"Optimize rule '{self.__class__.__name__}' is not implemented yet.")
