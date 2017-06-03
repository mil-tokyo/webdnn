from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.graph.operators.elu import Elu

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(relu_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(relu_Y_offset)%%;

    const int N = %%META_LOAD(relu_N)%%;
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = result < 0.0 ? (expf(result)-1) : result;      
        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def elu(op: Elu, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    meta_injector = MetaInjector()
    meta_injector.register({
        "relu_X_offset": x.offset,
        "relu_Y_offset": y.offset,
        "relu_N": y.variable.size
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        meta_injector.buffer
    )

    return [kernel]
