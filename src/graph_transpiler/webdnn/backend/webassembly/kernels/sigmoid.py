from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.sigmoid import Sigmoid

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(sigmoid_X)%%;
    float *Y = %%LOAD_BUFFER(sigmoid_Y)%%;

    const int N = %%LOAD_BUFFER(sigmoid_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        Y[gid] = 1.0F / (1.0F + expf(-X[gid]));
    }
}
"""


# noinspection PyUnusedLocal
def sigmoid(op: Sigmoid, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "sigmoid_X": x,
        "sigmoid_Y": y,
        "sigmoid_N": y.variable.size
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
