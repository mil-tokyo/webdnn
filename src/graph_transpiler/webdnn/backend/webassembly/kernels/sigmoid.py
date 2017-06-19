from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.sigmoid import Sigmoid

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(sigmoid_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(sigmoid_Y_offset)%%;

    const int N = %%META_LOAD(sigmoid_N)%%;

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

    meta_injector = MetaInjector()
    meta_injector.register({
        "sigmoid_X_offset": x.offset,
        "sigmoid_Y_offset": y.offset,
        "sigmoid_N": y.variable.size
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
