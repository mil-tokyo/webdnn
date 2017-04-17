from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu import attributes as A
from graph_builder.backend.webgpu.kernel import GPUSize, Kernel
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.operator import Operator

relu_source = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(relu_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(relu_Y_offset)%%;

    const int N = %%META_LOAD(relu_N)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        float result = X[gid];
        result = result < 0.0 ? 0.0 : result;      
        Y[gid] = %%ELEMENTWISE_ATTACHABLE(result)%%;
    }
}
"""


class Relu(Operator,
           A.Elementwise,
           A.ElementwiseAttachable):
    name: str = "relu"

    # noinspection PyMethodMayBeStatic
    def apply_elementwise_operation(self, expression: str) -> str:
        return "(({0}) >= 0.0 ? ({0}) : 0.0)".format(expression)

    def convert_to_kernels(self,
                           batch_size: int,
                           weights_layout: MemoryLayout,
                           variable_layout: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        num_output_element = self.layer.parameters["out_size"] * batch_size

        metabuffer_injector.register({
            "relu_X_offset": variable_layout.allocation_dict[self.inputs[0].name].offset,
            "relu_Y_offset": variable_layout.allocation_dict[self.outputs[0].name].offset,
            "relu_N": num_output_element
        })

        source = relu_source
        source = self.apply_elementwise_attach(source)
        source = metabuffer_injector.inject(source)

        func_name = Operator.add_canonical_suffix("relu", source)

        source = source.replace("%%FUNC_NAME%%", func_name)

        kernel = Kernel(
            {func_name: source},
            func_name,
            GPUSize(8, 1, 1),
            GPUSize(1024, 1, 1),
            metabuffer_injector.generate_buffer()
        )

        return [kernel]
