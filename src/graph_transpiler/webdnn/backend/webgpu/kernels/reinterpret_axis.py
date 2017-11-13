from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *x = %%LOAD_BUFFER(reinterpret_axis_x)%%;
    device float *y = %%LOAD_BUFFER(reinterpret_axis_y)%%;

    const int N = %%LOAD_BUFFER(reinterpret_axis_N)%%;

    for (int gid = index; gid < N; gid += num_threads) {
        y[gid] = x[gid];
    }
}
"""


@WebGPUDescriptorGenerator.register_handler(ReinterpretAxis)
def reinterpret_axis(op: ReinterpretAxis,
                     memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]
    if memory_layout[x] == memory_layout[y]:
        # This is inplace operation
        return []

    assert x.order == op.parameters["in_order"]
    assert y.order == op.parameters["out_order"]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "reinterpret_axis_x": memory_layout[x],
        "reinterpret_axis_y": memory_layout[y],
        "reinterpret_axis_N": y.size,
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(MAX_THREADS_PER_THREADGROUP, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
