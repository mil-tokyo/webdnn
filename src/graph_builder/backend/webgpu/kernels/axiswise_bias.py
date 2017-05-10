from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.inline_injector import InlineInjector
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.variables.attributes.order import OrderHWNC, OrderNHWC, OrderNC

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(axiswise_bias_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(axiswise_bias_Y_offset)%%;
    const device float *B = weight_buffer + %%META_LOAD(axiswise_bias_B_offset)%%;
    const int N = %%META_LOAD(axiswise_bias_N)%%;
    const int C = %%META_LOAD(axiswise_bias_C)%%;
  
    for (int gid = index; gid < N * C; gid += num_threads) {
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

    assert op.parameters["axis"] == Axis.C, "[WebGPU] AxiswiseBias supports only channelwise bias."

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
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
