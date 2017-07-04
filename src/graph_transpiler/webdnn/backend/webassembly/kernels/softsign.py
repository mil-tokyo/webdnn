from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.softsign import Softsign

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(softsign_X)%%;
    float *Y = %%LOAD_BUFFER(softsign_Y)%%;

    const int N = %%LOAD_BUFFER(softsign_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        float val = X[gid];
        Y[gid] = val / (fabsf(val) + 1.0F);
    }
}
"""


# noinspection PyUnusedLocal
def softsign(op: Softsign, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x0"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "softsign_X": x,
        "softsign_Y": y,
        "softsign_N": y.variable.size
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
