from abc import abstractmethod

from graph_builder.backend.webgpu.attributes.attribute import Attribute


class ElementwiseAttribute(Attribute):
    @abstractmethod
    def wrap_expression(self, expression: str) -> str:
        raise NotImplementedError
