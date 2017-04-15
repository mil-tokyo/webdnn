from abc import abstractmethod

from graph_builder.backend.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.backend.webgpu.attributes.attribute import Attribute


class NeedInitializeAttribute(Attribute):
    @abstractmethod
    def initialize(self,
                   meta_buffer: any,
                   params_allocation: WorkspaceLayoutWebGPU,
                   initialize_expression: str):
        raise NotImplementedError
