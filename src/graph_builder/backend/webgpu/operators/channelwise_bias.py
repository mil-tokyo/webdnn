from typing import List
import numpy as np

from graph_builder.backend.webgpu.attributes.elementwise import ElementwiseAttribute
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph import Layer, Variable
from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.attributes.channelwise import ChannelwiseAttribute
from graph_builder.backend.webgpu.attributes.need_initialize import NeedInitializeAttribute
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.webgpu.operators.operator import Operator, SerialGenerator


class ChannelwiseBias(Operator, ChannelwiseAttribute, NeedInitializeAttribute):
    name: str = "channelwise_bias"
    bias_name: str

    def initialize(self,
                   metabuffer_injector: MetaBufferInjector,
                   params_allocation: MemoryLayout,
                   initialize_expression: str):
        metabuffer_injector.register({
            "bias_offset": params_allocation.allocationDict[self.layer.name + "/b"].offset
        })
        initialize_expression += f"const device float *bias = param_buffer + %%META_LOAD(bias_offset)%%;"

        for child in self.children:
            if isinstance(child, NeedInitializeAttribute):
                initialize_expression += child.initialize(metabuffer_injector, params_allocation, initialize_expression)

        return initialize_expression

    def apply_channelwise_operation(self, expression: str, channel_index: str) -> str:
        expression = f"(({expression}) + (bias[{channel_index}]))"

        for child in self.children:
            if isinstance(child, ChannelwiseAttribute):
                expression = child.apply_channelwise_operation(expression, channel_index)

            if isinstance(child, ElementwiseAttribute):
                expression = child.apply_elementwise_operation(expression)

        return expression

    def convert_to_kernels(self,
                           batch_size: int,
                           params_allocation: MemoryLayout,
                           variable_allocation: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        raise NotImplementedError()
