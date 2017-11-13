from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%% )
{
    const float *x = %%LOAD_BUFFER(reinterpret_axis_x)%%;
    float *y = %%LOAD_BUFFER(reinterpret_axis_y)%%;

    const int N = %%LOAD_BUFFER(reinterpret_axis_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        y[gid] = x[gid];
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(ReinterpretAxis)
def reinterpret_axis(op: ReinterpretAxis, memory_layout: MemoryLayout) -> List[Kernel]:
    # Operation without need for transposition is currently supported
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
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
