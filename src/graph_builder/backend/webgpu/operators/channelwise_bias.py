from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu import attributes as A
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.operator import Operator

channelwise_bias_source = """
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
  
  for (int gid = index; gid < n; gid += 8192) {
    int out_chid = gid % out_ch;

    float val = input_data[gid] + param_data[out_chid];
    output_data[gid] = %%CHANNELWISE_ATTACHABLE(val, out_chid)%%;
  }
}
"""


class ChannelwiseBias(Operator,
                      A.Channelwise,
                      A.InitializerRequired,
                      A.ChannelwiseAttachable):
    name: str = "channelwise_bias"
    bias_name: str

    def apply_initializer(self,
                          metabuffer_injector: MetaBufferInjector,
                          params_allocation: MemoryLayout,
                          initialize_block: str):
        metabuffer_injector.register({
            "bias_offset": params_allocation.allocationDict[f"{self.layer.name}/b"].offset
        })
        return f"{initialize_block}\nconst device float *bias = param_buffer + %%META_LOAD(bias_offset)%%;"

    def apply_channelwise_operation(self, expression: str, channel_index: str) -> str:
        return f"(({expression}) + (bias[{channel_index}]))"

    def convert_to_kernels(self,
                           batch_size: int,
                           params_allocation: MemoryLayout,
                           variable_allocation: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        num_output_element = self.layer.parameters["out_size"] * batch_size

        metabuffer_injector.register({
            "input_data_offset": variable_allocation.allocationDict[self.inputs[0].name].offset,
            "output_data_offset": variable_allocation.allocationDict[self.outputs[0].name].offset,
            "param_data_offset": params_allocation.allocationDict[f"{self.layer.name}/b"].offset,
            "num_output_element": num_output_element,
            "num_out_ch": self.layer.parameters["out_size"]
        })

        source = channelwise_bias_source
        source = self.apply_channelwise_attach(source)
        source = metabuffer_injector.inject(source)

        func_name = Operator.add_canonical_suffix("channelwise_bias", source)

        source = source.replace("%%FUNC_NAME%%", func_name)

        kernel = Kernel(
            {func_name: source},
            func_name,
            GPUSize(8, 1, 1),
            GPUSize(1024, 1, 1),
            metabuffer_injector.generate_buffer()
        )

        return [kernel]
