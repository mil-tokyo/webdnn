from abc import abstractmethod

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.attributes.attribute import Attribute
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector


class NeedInitializeAttribute(Attribute):
    @abstractmethod
    def initialize(self,
                   metabuffer_injector: MetaBufferInjector,
                   params_allocation: MemoryLayout,
                   initialize_expression: str):
        raise NotImplementedError
