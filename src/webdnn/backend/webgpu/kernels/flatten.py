from typing import List

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.operators.flatten import Flatten

template = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *x = data_buffer + %%META_LOAD(flatten_x_offset)%%;
    device float *y = data_buffer + %%META_LOAD(flatten_y_offset)%%;

    const int N = %%META_LOAD(flatten_N)%%;

    for (int gid = index; gid < N; gid += num_threads) {
        y[gid] = x[gid];
    }
}
"""


def flatten(op: Flatten,
            constants_layout: MemoryLayout,
            variables_layout: MemoryLayout) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]

    # assert x.variable.order == y.variable.order

    meta_injector = MetaInjector()
    meta_injector.register({
        "flatten_x_offset": x.offset,
        "flatten_y_offset": y.offset,
        "flatten_N": y.variable.size,
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        meta_injector.buffer
    )

    return [kernel]
