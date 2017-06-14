from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.graph.operators.tanh import Tanh

template = """
kernel void %%FUNC_NAME%%(device float *data_buffer[[buffer(0)]],
                          const device int * %%META_NAME%% [[buffer(1)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(tanh_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(tanh_Y_offset)%%;

    const int N = %%META_LOAD(tanh_N)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        Y[gid] = tanh(X[gid]);
    }
}
"""


def tanh(op: Tanh,
         memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape
    assert x.variable.order == y.variable.order

    meta_injector = MetaInjector()
    meta_injector.register({
        "tanh_X_offset": x.offset,
        "tanh_Y_offset": y.offset,
        "tanh_N": y.variable.size
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
        meta_injector.buffer,
        meta_injector.unresolved_value_list
    )

    return [kernel]
