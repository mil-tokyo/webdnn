from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.hard_sigmoid import HardSigmoid

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(hard_sigmoid_X)%%;
    float *Y = %%LOAD_BUFFER(hard_sigmoid_Y)%%;

    const int N = %%LOAD_BUFFER(hard_sigmoid_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        float val = X[gid];
        val = val * 0.2F + 0.5F;
        if (val < 0.0F) {
            val = 0.0F;
        } else if (val > 1.0F) {
            val = 1.0F;
        }
        Y[gid] = val;
    }
}
"""


# noinspection PyUnusedLocal
def hard_sigmoid(op: HardSigmoid, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "hard_sigmoid_X": x,
        "hard_sigmoid_Y": y,
        "hard_sigmoid_N": y.variable.size
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
