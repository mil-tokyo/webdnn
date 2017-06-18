from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.flatten import Flatten

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%% )
{
    const float *x = %%LOAD_BUFFER(flatten_x)%%;
    float *y = %%LOAD_BUFFER(flatten_y)%%;

    const int N = %%LOAD_BUFFER(flatten_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        y[gid] = x[gid];
    }
}
"""


def flatten(op: Flatten, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "flatten_x": x,
        "flatten_y": y,
        "flatten_N": y.variable.size,
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
