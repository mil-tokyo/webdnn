from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.axiswise_scale import AxiswiseScale

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X0 = data_buffer + %%META_LOAD(elementwise_sum_X0_offset)%%;
    const float *X1 = data_buffer + %%META_LOAD(elementwise_sum_X1_offset)%%;
    float *Y = data_buffer + %%META_LOAD(elementwise_sum_Y_offset)%%;
    const int N = %%META_LOAD(elementwise_sum_N)%%;
  
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

    meta_injector = MetaInjector()
    meta_injector.register({
        "elementwise_sum_X0_offset": x0.offset,
        "elementwise_sum_X1_offset": x1.offset,
        "elementwise_sum_Y_offset": y.offset,
        "elementwise_sum_N": y.variable.size
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
