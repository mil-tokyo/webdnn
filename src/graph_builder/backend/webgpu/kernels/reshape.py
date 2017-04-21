from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators import Reshape


# noinspection PyUnusedLocal
def reshape(op: Reshape,
            constants_layout: MemoryLayout,
            variables_layout: MemoryLayout,
            metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    # do nothing
    return []
