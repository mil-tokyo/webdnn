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
                          uint index[[thread_position_in_grid]])
{
  device float *input_data = data_buffer + %%META_LOAD(input_data_offset)%%;
  device float *output_data = data_buffer + %%META_LOAD(output_data_offset)%%;

  const int n = %%META_LOAD(num_output_element)%%;
    for (int gid = index; gid < n; gid += 8192) {
      float val = input_data[gid];
      if (val < 0.0) {
        val = 0.0;
      }
      
      val = %%ELEMENTWISE_ATTACHABLE(val)%%;
      output_data[gid] = val;
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
                           params_allocation: MemoryLayout,
                           variable_allocation: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        num_output_element = self.layer.parameters["out_size"] * batch_size

        metabuffer_injector.register({
            "input_data_offset": variable_allocation.allocationDict[self.inputs[0].name].offset,
            "output_data_offset": variable_allocation.allocationDict[self.outputs[0].name].offset,
            "num_output_element": num_output_element
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
