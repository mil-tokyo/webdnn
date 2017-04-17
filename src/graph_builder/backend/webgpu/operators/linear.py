from typing import List

from graph_builder.backend.webgpu import attributes as A
from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.operator import Operator

linear_mul_source = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(linear_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(linear_Y_offset)%%;
    const device float *W = weight_buffer + %%META_LOAD(linear_W_offset)%%;
    const int M = %%META_LOAD(linear_M)%%;
    const int N = %%META_LOAD(linear_N)%%;
    const int K = %%META_LOAD(linear_K)%%;
    
    %%INITIALIZER_ATTACHABLE_PLACEHOLDER%%
  
    for (int gid = index; gid < M * N; gid += num_threads) {
        int n = gid % N;
        int m = gid / N;

        float sum = 0.0;
        for (int k = 0; k < K; k++) {
            sum += X[m * K + k] * W[k * N + n];
        }

        Y[gid] = %%CHANNELWISE_ATTACHABLE(sum, n)%%;
    }
}
"""


class Linear(Operator,
             A.ChannelwiseAttachable,
             A.InitializerAttachable):
    name: str = "linear"

    def convert_to_kernels(self,
                           batch_size: int,
                           weights_layout: MemoryLayout,
                           variable_layout: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        input_var = variable_layout.allocation_dict[self.inputs[0].name]
        output_var = variable_layout.allocation_dict[self.outputs[0].name]
        weight_var = weights_layout.allocation_dict[self.layer.name + "/W"]

        metabuffer_injector.register({
            "linear_X_offset": input_var.offset,
            "linear_Y_offset": output_var.offset,
            "linear_W_offset": weight_var.offset,
            "linear_M": batch_size,
            "linear_N": self.layer.parameters["out_size"],
            "linear_K": self.layer.parameters["in_size"],
        })

        source = linear_mul_source
        source = self.apply_initializer_attach(metabuffer_injector, weights_layout, source)
        source = self.apply_channelwise_attach(source)
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
