from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
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


def reinterpret_axis(op: ReinterpretAxis, memory_layout: MemoryLayout) -> List[Kernel]:
    # Operation without need for transposition is currently supported
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == op.parameters["in_order"]
    assert y.variable.order == op.parameters["out_order"]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "reinterpret_axis_x": x,
        "reinterpret_axis_y": y,
        "reinterpret_axis_N": y.variable.size,
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
