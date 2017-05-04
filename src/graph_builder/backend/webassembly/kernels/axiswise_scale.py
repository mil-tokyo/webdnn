from typing import List

from graph_builder.backend.webassembly.allocator import MemoryLayout
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.backend.webassembly.kernels import util
from graph_builder.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderNC, OrderHWNC

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(axiswise_scale_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(axiswise_scale_Y_offset)%%;
    const float *S = weight_buffer + %%META_LOAD(axiswise_scale_S_offset)%%;
    const int N = %%META_LOAD(axiswise_scale_N)%%;
    const int C = %%META_LOAD(axiswise_scale_C)%%;
  
    for (int gid = 0; gid < N; gid += 1) {
        int c = gid % C;

        float result = X[gid] * S[c];
        //Y[gid] = %%CHANNELWISE_ATTACHABLE(result, c)%%;
        Y[gid] = result;
    }
}
"""


def axiswise_scale(op: AxiswiseScale,
                   constants_layout: MemoryLayout,
                   variables_layout: MemoryLayout,
                   metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    s = constants_layout[op.inputs["s"]]
    y = variables_layout[op.outputs["y"]]

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    assert x.variable.axis_order == OrderNC or x.variable.axis_order == OrderNHWC or x.variable.axis_order == OrderHWNC
    assert y.variable.axis_order == OrderNC or y.variable.axis_order == OrderNHWC or y.variable.axis_order == OrderHWNC
    assert op.parameters["axis"] == Axis.C, "[Webassembly] AxiswiseScale supports only channelwise bias."

    metabuffer_injector.register({
        "axiswise_scale_X_offset": x.offset,
        "axiswise_scale_Y_offset": y.offset,
        "axiswise_scale_S_offset": s.offset,
        "axiswise_scale_N": y.variable.size,
        "axiswise_scale_C": y.variable.shape_dict[Axis.C],
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("axiswise_scale", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
