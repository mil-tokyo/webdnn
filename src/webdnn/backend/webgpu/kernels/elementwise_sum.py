from typing import List

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.inline_injector import InlineInjector
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.operators.axiswise_scale import AxiswiseScale

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X0 = data_buffer + %%META_LOAD(elementwise_sum_X0_offset)%%;
    const device float *X1 = data_buffer + %%META_LOAD(elementwise_sum_X1_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(elementwise_sum_Y_offset)%%;
    const int N = %%META_LOAD(elementwise_sum_N)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        float result = X0[gid] + X1[gid];

        Y[gid] = %%INLINE(result)%%;
    }
}
"""


def elementwise_sum(op: AxiswiseScale,
                    constants_layout: MemoryLayout,
                    variables_layout: MemoryLayout) -> List[Kernel]:
    x0 = variables_layout[op.inputs["x0"]]
    x1 = variables_layout[op.inputs["x1"]]
    y = variables_layout[op.outputs["y"]]

    assert len(op.inputs) == 2, "[WebGPU] ElementwiseSum operator currently supported only 2 inputs."
    assert x0.variable.shape == x1.variable.shape == y.variable.shape

    meta_injector = MetaInjector()
    meta_injector.register({
        "elementwise_sum_X0_offset": x0.offset,
        "elementwise_sum_X1_offset": x1.offset,
        "elementwise_sum_Y_offset": y.offset,
        "elementwise_sum_N": y.variable.size
    })

    inline_injector = InlineInjector(op)
    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = inline_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        meta_injector.buffer
    )

    return [kernel]
