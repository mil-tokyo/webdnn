from typing import List
import numpy as np
from graph_builder.graph import Layer, Variable
from graph_builder.backend.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.backend.webgpu.attributes.channelwise import ChannelwiseAttribute
from graph_builder.backend.webgpu.attributes.need_initialize import NeedInitializeAttribute
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.webgpu.operators.operator import Operator, SerialGenerator


class ChannelwiseBias(Operator, ChannelwiseAttribute, NeedInitializeAttribute):
    bias_name: str

    def __init__(self,
                 layer: Layer,
                 serial_generator: SerialGenerator,
                 name: str = "bias"):
        super().__init__(layer, serial_generator, name)
        self.bias_name = serial_generator('bias')

    def initialize(self,
                   meta_buffer: any,
                   params_allocation: WorkspaceLayoutWebGPU,
                   initialize_expression: str):
        meta_buffer += np.array([params_allocation.allocationDict[self.layer.name + "/b"].offset], dtype=np.int32).tobytes()
        initialize_expression += "const device float *{0} = param_buffer + %%LOAD_META(bias_offset)%%;".format(self.bias_name)

        return initialize_expression

    def wrap_expression(self, expression: str, channel_index: str) -> str:
        return "(({0}) + ({1}[{2}]))".format(expression, self.bias_name, channel_index)

    def generate_kernel_self(self,
                             batch_size: int,
                             inputs: List[Variable], tops: List[Variable],
                             params_allocation: WorkspaceLayoutWebGPU,
                             variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:
        raise NotImplementedError()
