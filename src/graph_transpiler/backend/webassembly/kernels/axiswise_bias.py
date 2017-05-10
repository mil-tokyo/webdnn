from typing import List

from graph_transpiler.backend.webgpu.allocator import MemoryLayout
from graph_transpiler.backend.webassembly.inline_injector import InlineInjector
from graph_transpiler.backend.webassembly.kernel import Kernel
from graph_transpiler.backend.webassembly.kernels import util
from graph_transpiler.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.operators.axiswise_bias import AxiswiseBias
from graph_transpiler.graph.variables.attributes.order import OrderHWNC, OrderNHWC, OrderNC

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(axiswise_bias_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(axiswise_bias_Y_offset)%%;
    const float *B = weight_buffer + %%META_LOAD(axiswise_bias_B_offset)%%;
    const int N = %%META_LOAD(axiswise_bias_N)%%;
    const int C = %%META_LOAD(axiswise_bias_C)%%;
  
    for (int gid = 0; gid < N * C; gid += 1) {
        int c = gid % C;
        int n = gid / C;

        float result = X[gid] + B[c];
        Y[n * C + c] = %%INLINE(result)%%;
    }
}
"""


def axiswise_bias(op: AxiswiseBias,
                  constants_layout: MemoryLayout,
                  variables_layout: MemoryLayout,
                  metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    b = constants_layout[op.inputs["b"]]
    y = variables_layout[op.outputs["y"]]

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    assert x.variable.order == OrderNC or x.variable.order == OrderNHWC or x.variable.order == OrderHWNC
    assert y.variable.shape == x.variable.shape

    assert op.parameters["axis"] == Axis.C, "[Webassembly] AxiswiseBias supports only channelwise bias."

    metabuffer_injector.register({
        "axiswise_bias_X_offset": x.offset,
        "axiswise_bias_Y_offset": y.offset,
        "axiswise_bias_B_offset": b.offset,
        "axiswise_bias_N": y.variable.size // y.variable.shape_dict[Axis.C],
        "axiswise_bias_C": y.variable.shape_dict[Axis.C],
    })

    inline_injector = InlineInjector()
    if "inline_elementwise" in op.parameters:
        inline_injector.delegate = op.parameters["inline_elementwise"]

    source = template
    source = metabuffer_injector.inject(source)
    source = inline_injector.inject(source)
    func_name = util.add_canonical_suffix("axiswise_bias", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
