from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.softplus import Softplus

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(softplus_X)%%;
    float *Y = %%LOAD_BUFFER(softplus_Y)%%;

    const int N = %%LOAD_BUFFER(softplus_N)%%;
    const float beta = *((const float *)(& %%LOAD_BUFFER(softplus_beta)%%));
    const float beta_inv = 1.0 / beta;

    for (int gid = 0; gid < N; gid += 1) {
        float val = X[gid];
        Y[gid] = logf(1.0F + expf(beta * val)) * beta_inv;
    }
}
"""


# noinspection PyUnusedLocal
def softplus(op: Softplus, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x0"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "softplus_X": x,
        "softplus_Y": y,
        "softplus_N": y.variable.size,
        "softplus_beta": op.parameters["beta"]
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
