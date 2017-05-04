from typing import List

from graph_builder.backend.webassembly.allocator import MemoryLayout
from graph_builder.backend.webassembly.inline_injector import InlineInjector
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.backend.webassembly.kernels import util
from graph_builder.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X0 = data_buffer + %%META_LOAD(elementwise_sum_X0_offset)%%;
    const float *X1 = data_buffer + %%META_LOAD(elementwise_sum_X1_offset)%%;
    float *Y = data_buffer + %%META_LOAD(elementwise_sum_Y_offset)%%;
    const int N = %%META_LOAD(elementwise_sum_N)%%;
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X0[gid] + X1[gid];
        //Y[gid] = %%CHANNELWISE_ATTACHABLE(result, c)%%;
        Y[gid] = %%INLINE(result)%%;
    }
}
"""


# noinspection PyUnusedLocal
def elementwise_sum(op: AxiswiseScale,
                    constants_layout: MemoryLayout,
                    variables_layout: MemoryLayout,
                    metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x0 = variables_layout[op.inputs["x0"]]
    x1 = variables_layout[op.inputs["x1"]]
    y = variables_layout[op.outputs["y"]]

    assert len(op.inputs) == 2, "[Webassembly] ElementwiseSum operator currently supported only 2 inputs."
    assert x0.variable.shape == x1.variable.shape == y.variable.shape

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    metabuffer_injector.register({
        "elementwise_sum_X0_offset": x0.offset,
        "elementwise_sum_X1_offset": x1.offset,
        "elementwise_sum_Y_offset": y.offset,
        "elementwise_sum_N": y.variable.size
    })

    inline_injector = InlineInjector()
    if "inline_elementwise" in op.parameters:
        inline_injector.delegate = op.parameters["inline_elementwise"]

    source = template
    source = metabuffer_injector.inject(source)
    source = inline_injector.inject(source)
    func_name = util.add_canonical_suffix("elementwise_sum", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
