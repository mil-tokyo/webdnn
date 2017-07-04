from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.clipped_relu import ClippedRelu

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(clipped_relu_X)%%;
    float *Y = %%LOAD_BUFFER(clipped_relu_Y)%%;

    const int N = %%LOAD_BUFFER(clipped_relu_N)%%;
    const float cap = *((const float *)(& %%LOAD_BUFFER(clipped_relu_cap)%%));

    for (int gid = 0; gid < N; gid += 1) {
        float val = X[gid];
        Y[gid] = val >= 0.0F ? (val < cap ? val : cap) : 0.0F;
    }
}
"""


# noinspection PyUnusedLocal
def clipped_relu(op: ClippedRelu, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x0"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "clipped_relu_X": x,
        "clipped_relu_Y": y,
        "clipped_relu_N": y.variable.size,
        "clipped_relu_cap": op.parameters["cap"]
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
