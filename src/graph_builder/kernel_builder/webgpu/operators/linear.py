from collections import OrderedDict

from typing import List
import numpy as np
from graph_builder.graph import Layer, Variable
from graph_builder.kernel_builder.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.kernel_builder.webgpu.kernel import Kernel, GPUSize
from graph_builder.kernel_builder.webgpu.operators.attributes import KBLayerAttribute
from graph_builder.kernel_builder.webgpu.operators.layer import KBLayer, KBKernelSerialGenerator

linear_mul_source = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int *meta_buffer[[buffer(2)]],
                          uint index[[thread_position_in_grid]])
{
  device float *input_data = data_buffer + (*meta_buffer++);
  device float *output_data = data_buffer + (*meta_buffer++);
  const device float *param_data = param_buffer + (*meta_buffer++);
  const int n = (*meta_buffer++);
  const int out_ch = (*meta_buffer++);
  const int in_ch = (*meta_buffer++);
  %%POST_INIT%%
    for (int gid = index; gid < n; gid += 4096) {
      int out_chid = gid % out_ch;
      int sample_id = gid / out_ch;
      float sum = 0.0;
      for (int in_chid = 0; in_chid < in_ch; in_chid++) {
        sum += input_data[sample_id * in_ch + in_chid] * param_data[in_chid * out_ch + out_chid];
      }
      output_data[gid] = %%MAKE_OUTPUT%%;
    }
}
"""


class KBLinearLayer(KBLayer):
    def __init__(self, layer: Layer):
        super().__init__(layer, "linear", set())

    def generate_kernels(self,
                         batch_size: int,
                         bottoms: List[Variable],
                         tops: List[Variable],
                         params_allocation: WorkspaceLayoutWebGPU,
                         variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:

        input_var = variable_allocation.allocationDict[bottoms[0].name]
        output_var = variable_allocation.allocationDict[tops[0].name]
        param_var = params_allocation.allocationDict[self.layer.name + "/W"]

        num_output_elem = batch_size * self.layer.parameters["out_size"]
        meta_array = np.array([
            input_var.offset, output_var.offset, param_var.offset,
            num_output_elem, self.layer.parameters["out_size"], self.layer.parameters["in_size"]
        ], dtype=np.int32)
        meta_buffer = meta_array.tobytes()

        threadgroups_per_grid = GPUSize(8, 1, 1)
        threads_per_thread_group = GPUSize(512, 1, 1)
        sources = OrderedDict()  # to preserve order
        func_name = "linear_mul_"
        make_output = "sum"
        post_init_source = ""
        serial_generator = KBKernelSerialGenerator()

        # FIXME: iteratorを用いて木構造・グラフ構造をiterationできるように。
        for child in self.children:
            if KBLayerAttribute.Elementwise in child.attributes:
                elementwise_operator = child.get_elementwise_operator(params_allocation, serial_generator)
                post_init_source += elementwise_operator.post_init_source
                make_output = elementwise_operator.wrap_expression(make_output)
                func_name += child.name + "_"
                sources.update(elementwise_operator.sources)
                meta_buffer += elementwise_operator.meta_buffer

            elif KBLayerAttribute.Channelwise in child.attributes:
                channelwise_operator = child.get_channelwise_operator(params_allocation, serial_generator)
                post_init_source += channelwise_operator.post_init_source
                make_output = channelwise_operator.wrap_expression(make_output)
                func_name += child.name + "_"
                sources.update(channelwise_operator.sources)
                meta_buffer += channelwise_operator.meta_buffer

            else:
                raise NotImplementedError()

        sources[func_name] = linear_mul_source.replace("%%POST_INIT%%", post_init_source) \
            .replace("%%FUNC_NAME%%", func_name) \
            .replace("%%MAKE_OUTPUT%%", make_output)

        kernel = Kernel(sources, func_name, threadgroups_per_grid, threads_per_thread_group, meta_buffer)

        return [kernel]
