from abc import abstractmethod

from graph_builder.backend.webgpu.attributes.attribute import Attribute


class Elementwise(Attribute):
    @abstractmethod
    def apply_elementwise_operation(self, expression: str) -> str:
        raise NotImplementedError
