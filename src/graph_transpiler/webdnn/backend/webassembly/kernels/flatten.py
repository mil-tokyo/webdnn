from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.graph.operators.flatten import Flatten

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%% )
{
    const float *x = data_buffer + %%META_LOAD(flatten_x_offset)%%;
    float *y = data_buffer + %%META_LOAD(flatten_y_offset)%%;

    const int N = %%META_LOAD(flatten_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        y[gid] = x[gid];
    }
}
"""


def flatten(op: Flatten, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

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
        meta_injector.buffer
    )

    return [kernel]
