from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.order import OrderHWNC, OrderNHWC, OrderNC

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(axiswise_bias_X)%%;
    float *Y = %%LOAD_BUFFER(axiswise_bias_Y)%%;
    const float *B = %%LOAD_BUFFER(axiswise_bias_B)%%;
    const int N = %%LOAD_BUFFER(axiswise_bias_N)%%;
    const int C = %%LOAD_BUFFER(axiswise_bias_C)%%;
  
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

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "axiswise_bias_X": x,
        "axiswise_bias_Y": y,
        "axiswise_bias_B": b,
        "axiswise_bias_N": y.variable.size // y.variable.shape_dict[Axis.C],
        "axiswise_bias_C": y.variable.shape_dict[Axis.C],
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
