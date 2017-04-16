from abc import abstractmethod

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.attributes import InitializerRequired
from graph_builder.backend.webgpu.attributes.attribute import Attribute
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.tag_parser import TagParser


class InitializerAttachable(Attribute):
    def apply_initializer_attach(self,
                                 metabuffer_injector: MetaBufferInjector,
                                 weights_layout: MemoryLayout,
                                 source: str) -> str:
        block = ""
        for tag in TagParser.parse(source):
            if tag.name == "INITIALIZER_ATTACHABLE_PLACEHOLDER":
                # noinspection PyUnresolvedReferences
                for child in self.iter_children_all():
                    if isinstance(child, InitializerRequired):
                        block = child.apply_initializer(metabuffer_injector, weights_layout, block)

                source = source[:tag.span[0]] + block + source[tag.span[1]:]

        return source
