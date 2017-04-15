from collections import OrderedDict

import numpy as np
from typing import List

from graph_builder.graph import Layer, Variable
from graph_builder.backend.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.backend.webgpu.attributes.channelwise import ChannelwiseAttribute
from graph_builder.backend.webgpu.attributes.elementwise import ElementwiseAttribute
from graph_builder.backend.webgpu.attributes.need_initialize import NeedInitializeAttribute
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.operators.operator import Operator, SerialGenerator

linear_mul_source = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int *meta_buffer[[buffer(2)]],
                          uint index[[thread_position_in_grid]])
{
    device float *input_data = data_buffer + %%LOAD_META(meta_buffer, input_data_offset)%%;
    device float *output_data = data_buffer + %%LOAD_META(meta_buffer, output_data_offset)%%;
    const device float *param_data = param_buffer + %%LOAD_META(meta_buffer, param_data_offset)%%;
    const int n = (*meta_buffer++);
    const int out_ch = (*meta_buffer++);
    const int in_ch = (*meta_buffer++);
    
    %%INITIALIZE_EXPRESSION%%
  
    for (int gid = index; gid < n; gid += 4096) {
        int out_chid = gid % out_ch;
        int sample_id = gid / out_ch;
        float sum = 0.0;
        for (int in_chid = 0; in_chid < in_ch; in_chid++) {
            sum += input_data[sample_id * in_ch + in_chid] * param_data[in_chid * out_ch + out_chid];
        }
        output_data[gid] = %%OUTPUT_EXPRESSION%%;
    }
}
"""


class Linear(Operator):
    def __init__(self,
                 layer: Layer,
                 serial_generator: SerialGenerator,
                 name: str = "linear"):
        super().__init__(layer, serial_generator, name)

    def generate_kernel_self(self,
                             batch_size: int,
                             inputs: List[Variable],
                             outputs: List[Variable],
                             params_allocation: WorkspaceLayoutWebGPU,
                             variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:

        input_var = variable_allocation.allocationDict[inputs[0].name]
        output_var = variable_allocation.allocationDict[outputs[0].name]
        param_var = params_allocation.allocationDict[self.layer.name + "/W"]

        meta_buffer = np.array([
            input_var.offset,
            output_var.offset,
            param_var.offset,
            batch_size * self.layer.parameters["out_size"],
            self.layer.parameters["out_size"],
            self.layer.parameters["in_size"]
        ], dtype=np.int32).tobytes()

        threadgroups_per_grid = GPUSize(8, 1, 1)
        threads_per_thread_group = GPUSize(512, 1, 1)

        sources = OrderedDict()  # to preserve order
        func_name = "linear_mul_"

        initialize_expression = ""
        output_expression = "sum"

        # FIXME: iteratorを用いて木構造・グラフ構造をiterationできるように。
        for child in self.children:
            if isinstance(child, ElementwiseAttribute):
                output_expression = child.wrap_expression(output_expression)
                func_name += child.name + "_"

            if isinstance(child, ChannelwiseAttribute):
                output_expression = child.wrap_expression(output_expression, "out_chid")
                func_name += child.name + "_"

            if isinstance(child, NeedInitializeAttribute):
                initialize_expression = child.initialize(meta_buffer, params_allocation, initialize_expression)
                func_name += child.name + "_"

        sources[func_name] = linear_mul_source \
            .replace("%%INITIALIZE_EXPRESSION%%", initialize_expression) \
            .replace("%%OUTPUT_EXPRESSION%%", output_expression) \
            .replace("%%FUNC_NAME%%", func_name)

        kernel = Kernel(sources, func_name, threadgroups_per_grid, threads_per_thread_group, meta_buffer)

        return [kernel]
