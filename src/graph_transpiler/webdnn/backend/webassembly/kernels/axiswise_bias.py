from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.order import OrderHWNC, OrderNHWC, OrderNC

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(axiswise_bias_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(axiswise_bias_Y_offset)%%;
    const float *B = data_buffer + %%META_LOAD(axiswise_bias_B_offset)%%;
    const int N = %%META_LOAD(axiswise_bias_N)%%;
    const int C = %%META_LOAD(axiswise_bias_C)%%;
  
    for (int gid = 0; gid < N * C; gid += 1) {
        int c = gid % C;
        int n = gid / C;
        float result = X[gid] + B[c];

        Y[n * C + c] = result;
    }
}
"""


def axiswise_bias(op: AxiswiseBias, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    b = memory_layout[op.inputs["b"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNC or x.variable.order == OrderNHWC or x.variable.order == OrderHWNC
    assert y.variable.shape == x.variable.shape

    assert op.parameters["axis"] == Axis.C, "[Webassembly] AxiswiseBias supports only channelwise bias."

    meta_injector = MetaInjector()
    meta_injector.register({
        "axiswise_bias_X_offset": x.offset,
        "axiswise_bias_Y_offset": y.offset,
        "axiswise_bias_B_offset": b.offset,
        "axiswise_bias_N": y.variable.size // y.variable.shape_dict[Axis.C],
        "axiswise_bias_C": y.variable.shape_dict[Axis.C],
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
