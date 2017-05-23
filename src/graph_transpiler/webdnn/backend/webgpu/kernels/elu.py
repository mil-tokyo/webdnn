from typing import List

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.graph.operators.elu import Elu

template = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(elu_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(elu_Y_offset)%%;

    const int N = %%META_LOAD(elu_N)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        float result = X[gid];
        result = result < 0.0 ? (exp(result)-1) : result;      

        Y[gid] = result;
    }
}
"""


def elu(op: Elu,
        constants_layout: MemoryLayout,
        variables_layout: MemoryLayout) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    meta_injector = MetaInjector()
    meta_injector.register({
        "elu_X_offset": x.offset,
        "elu_Y_offset": y.offset,
        "elu_N": y.variable.size
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
