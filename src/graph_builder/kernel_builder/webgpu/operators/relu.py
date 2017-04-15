from typing import List
import numpy as np

from graph_builder.graph import Variable, Layer
from graph_builder.kernel_builder.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.kernel_builder.webgpu.kernel import GPUSize, Kernel
from graph_builder.kernel_builder.webgpu.operators.attributes import KBLayerAttribute
from graph_builder.kernel_builder.webgpu.operators.elementwise import KBElementwiseOperator
from graph_builder.kernel_builder.webgpu.operators.layer import KBLayer, KBKernelSerialGenerator

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
  device float *input_data = data_buffer + meta_buffer[0];
  device float *output_data = data_buffer + meta_buffer[1];
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


class KBReluLayer(KBLayer):
    def __init__(self, layer: Layer):
        super().__init__(layer, "relu", {KBLayerAttribute.Elementwise})

    # noinspection PyMethodMayBeStatic
    def get_elementwise_operator(self, params_allocation: WorkspaceLayoutWebGPU, serial_generator: KBKernelSerialGenerator):
        return KBElementwiseOperator("elementwise_relu", {"elementwise_relu": elementwise_relu_source}, serial_generator)

    def generate_kernels(self, batch_size: int,
                         bottoms: List[Variable], tops: List[Variable],
                         params_allocation: WorkspaceLayoutWebGPU, variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:
        layer = self.layer
        n = layer.parameters["out_size"] * batch_size
        bottom_av = variable_allocation.allocationDict[bottoms[0].name]
        top_av = variable_allocation.allocationDict[tops[0].name]
        meta_array = np.array([bottom_av.offset, top_av.offset, n], dtype=np.int32)
        meta_buffer = meta_array.tobytes()
        threadgroups_per_grid = GPUSize(8, 1, 1)
        threads_per_thread_group = GPUSize(512, 1, 1)

        kernel = Kernel({"relu": relu_source}, "relu", threadgroups_per_grid, threads_per_thread_group,
                        meta_buffer)
        return [kernel]
