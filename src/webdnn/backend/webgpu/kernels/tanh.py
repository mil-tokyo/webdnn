from typing import List

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.graph.operators.tanh import Tanh

template = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
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
         constants_layout: MemoryLayout,
         variables_layout: MemoryLayout) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]

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
        meta_injector.buffer
    )

    return [kernel]
