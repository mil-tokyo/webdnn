from collections import OrderedDict
from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.attributes.channelwise import ChannelwiseAttribute
from graph_builder.backend.webgpu.attributes.elementwise import ElementwiseAttribute
from graph_builder.backend.webgpu.attributes.need_initialize import NeedInitializeAttribute
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.operator import Operator

linear_mul_source = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]])
{
    device float *input_data = data_buffer + %%META_LOAD(input_data_offset)%%;
    device float *output_data = data_buffer + %%META_LOAD(output_data_offset)%%;
    const device float *param_data = param_buffer + %%META_LOAD(param_data_offset)%%;
    const int n = %%META_LOAD(num_output_element)%%;
    const int out_ch = %%META_LOAD(num_out_ch)%%;
    const int in_ch = %%META_LOAD(num_in_ch)%%;
    
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
    name: str = "linear"

    def convert_to_kernels(self,
                           batch_size: int,
                           params_allocation: MemoryLayout,
                           variable_allocation: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:

        input_var = variable_allocation.allocationDict[self.inputs[0].name]
        output_var = variable_allocation.allocationDict[self.outputs[0].name]
        param_var = params_allocation.allocationDict[self.layer.name + "/W"]

        metabuffer_injector.register({
            "input_data_offset": input_var.offset,
            "output_data_offset": output_var.offset,
            "param_data_offset": param_var.offset,
            "num_output_element": batch_size * self.layer.parameters["out_size"],
            "num_out_ch": self.layer.parameters["out_size"],
            "num_in_ch": self.layer.parameters["in_size"],
        })

        sources = OrderedDict()  # to preserve order
        initialize_expression = ""
        output_expression = "sum"

        for child in self.children:
            if isinstance(child, ElementwiseAttribute):
                output_expression = child.apply_elementwise_operation(output_expression)

            if isinstance(child, ChannelwiseAttribute):
                output_expression = child.apply_channelwise_operation(output_expression, "out_chid")

            if isinstance(child, NeedInitializeAttribute):
                initialize_expression = child.initialize(metabuffer_injector, params_allocation, initialize_expression)

        source = linear_mul_source \
            .replace("%%INITIALIZE_EXPRESSION%%", initialize_expression) \
            .replace("%%OUTPUT_EXPRESSION%%", output_expression)
        source = metabuffer_injector.inject(source)

        func_name = Operator.add_canonical_suffix("linear", source)

        source = source.replace("%%FUNC_NAME%%", func_name)

        kernel = Kernel(
            {func_name: source},
            func_name,
            GPUSize(8, 1, 1),
            GPUSize(512, 1, 1),
            metabuffer_injector.generate_buffer()
        )

        return [kernel]
