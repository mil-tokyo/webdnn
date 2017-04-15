import numpy as np
from typing import List

from graph_builder.graph import Variable, Layer
from graph_builder.backend.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.backend.webgpu.attributes.elementwise import ElementwiseAttribute
from graph_builder.backend.webgpu.kernel import GPUSize, Kernel
from graph_builder.backend.webgpu.operators.operator import Operator, SerialGenerator

elementwise_relu_source = """
float elementwise_relu(float x)
{
    return x >= 0.0 ? x : 0.0;
}
"""

relu_source = """
kernel void relu(const device float *param_buffer[[buffer(0)]],
                 device float *data_buffer[[buffer(1)]],
                 const device int *meta_buffer[[buffer(2)]],
                  uint index[[thread_position_in_grid]])
{
  device float *input_data = data_buffer + %%LOAD_META(meta_buffer, input_data_offset)%%;
  device float *output_data = data_buffer + %%LOAD_META(meta_buffer, output_data_offset)%%;
  const int n = meta_buffer[2];
    for (int gid = index; gid < n; gid += 4096) {
      float val = input_data[gid];
      if (val < 0.0) {
        val = 0.0;
      }
      output_data[gid] = val;
    }
}
"""


class Relu(Operator, ElementwiseAttribute):
    def __init__(self,
                 layer: Layer,
                 serial_generator: SerialGenerator,
                 name: str = "relu"):
        super().__init__(layer, serial_generator, name)

    # noinspection PyMethodMayBeStatic
    def wrap_expression(self, expression: str) -> str:
        return "(({0}) >= 0.0 ? ({0}) : 0.0)".format(expression)

    def generate_kernel_self(self, batch_size: int,
                             inputs: List[Variable],
                             outputs: List[Variable],
                             params_allocation: WorkspaceLayoutWebGPU,
                             variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:
        layer = self.layer
        num_output_element = layer.parameters["out_size"] * batch_size

        meta_array = np.array([
            variable_allocation.allocationDict[inputs[0].name].offset,
            variable_allocation.allocationDict[outputs[0].name].offset,
            num_output_element
        ], dtype=np.int32)

        meta_buffer = meta_array.tobytes()
        threadgroups_per_grid = GPUSize(8, 1, 1)
        threads_per_thread_group = GPUSize(512, 1, 1)

        kernel = Kernel(
            {"relu": relu_source},
            "relu",
            threadgroups_per_grid,
            threads_per_thread_group,
            meta_buffer
        )

        return [kernel]
