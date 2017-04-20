from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators import Reshape
from graph_builder.graph.operators.attributes import Axis
from graph_builder.graph.variables import attributes as VA

template = """
"""


def reshape(op: Reshape,
            constants_layout: MemoryLayout,
            variables_layout: MemoryLayout,
            metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    raise NotImplementedError()
