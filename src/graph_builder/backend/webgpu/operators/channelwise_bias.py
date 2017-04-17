from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu import attributes as A
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.operator import Operator

channelwise_bias_source = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(channelwise_bias_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(channelwise_bias_Y_offset)%%;
    const device float *B = weight_buffer + %%META_LOAD(channelwise_bias_B_offset)%%;
    const int N = %%META_LOAD(channelwise_bias_N)%%;
    const int C = %%META_LOAD(channelwise_bias_C)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        int c = gid % C;

        float result = X[gid] + B[c];
        Y[gid] = %%CHANNELWISE_ATTACHABLE(result, c)%%;
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
                          weights_allocation: MemoryLayout,
                          initialize_block: str):
        metabuffer_injector.register({
            "channelwise_bias_B_offset": weights_allocation.allocation_dict[f"{self.layer.name}/b"].offset
        })
        return f"{initialize_block}\nconst device float *bias = weight_buffer + %%META_LOAD(channelwise_bias_B_offset)%%;"

    def apply_channelwise_operation(self, expression: str, channel_index: str) -> str:
        return f"(({expression}) + (bias[{channel_index}]))"

    def convert_to_kernels(self,
                           batch_size: int,
                           weights_layout: MemoryLayout,
                           variable_layout: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        num_output_element = self.layer.parameters["out_size"] * batch_size

        metabuffer_injector.register({
            "channelwise_bias_X_offset": variable_layout.allocation_dict[self.inputs[0].name].offset,
            "channelwise_bias_Y_offset": variable_layout.allocation_dict[self.outputs[0].name].offset,
            "channelwise_bias_B_offset": weights_layout.allocation_dict[f"{self.layer.name}/b"].offset,
            "channelwise_bias_N": num_output_element,
            "channelwise_bias_C": self.layer.parameters["out_size"]
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
