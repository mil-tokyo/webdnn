from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.axiswise_scale import AxiswiseScale

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X0 = %%LOAD_BUFFER(elementwise_sum_X0)%%;
    const float *X1 = %%LOAD_BUFFER(elementwise_sum_X1)%%;
    float *Y = %%LOAD_BUFFER(elementwise_sum_Y)%%;
    const int N = %%LOAD_BUFFER(elementwise_sum_N)%%;
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X0[gid] + X1[gid];

        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def elementwise_sum(op: AxiswiseScale, memory_layout: MemoryLayout) -> List[Kernel]:
    x0 = memory_layout[op.inputs["x0"]]
    x1 = memory_layout[op.inputs["x1"]]
    y = memory_layout[op.outputs["y"]]

    assert len(op.inputs) == 2, "[Webassembly] ElementwiseSum operator currently supported only 2 inputs."
    assert x0.variable.shape == x1.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "elementwise_sum_X0": x0,
        "elementwise_sum_X1": x1,
        "elementwise_sum_Y": y,
        "elementwise_sum_N": y.variable.size
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
