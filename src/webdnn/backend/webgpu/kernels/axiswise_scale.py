from typing import List

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.axis import Axis
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.order import OrderNHWC, OrderNC, OrderHWNC

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(axiswise_scale_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(axiswise_scale_Y_offset)%%;
    const device float *S = weight_buffer + %%META_LOAD(axiswise_scale_S_offset)%%;
    const int N = %%META_LOAD(axiswise_scale_N)%%;
    const int C = %%META_LOAD(axiswise_scale_C)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        int c = gid % C;

        float result = X[gid] * S[c];

        Y[gid] = result;
    }
}
"""


def axiswise_scale(op: AxiswiseScale,
                   constants_layout: MemoryLayout,
                   variables_layout: MemoryLayout) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    s = constants_layout[op.inputs["s"]]
    y = variables_layout[op.outputs["y"]]

    assert x.variable.order == OrderNC or x.variable.order == OrderNHWC or x.variable.order == OrderHWNC
    assert y.variable.order == OrderNC or y.variable.order == OrderNHWC or y.variable.order == OrderHWNC
    assert op.parameters["axis"] == Axis.C, "[WebGPU] AxiswiseScale supports only channelwise bias."

    meta_injector = MetaInjector()
    meta_injector.register({
        "axiswise_scale_X_offset": x.offset,
        "axiswise_scale_Y_offset": y.offset,
        "axiswise_scale_S_offset": s.offset,
        "axiswise_scale_N": y.variable.size,
        "axiswise_scale_C": y.variable.shape_dict[Axis.C],
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        meta_injector.buffer
    )

    return [kernel]
